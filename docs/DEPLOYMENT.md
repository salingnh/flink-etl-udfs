# Deploying `flink-etl-udfs` to Apache Flink

## Dependency profile — 0.6.0

- `flink_etl_udfs.core.*`: Python standard library only.
- `flink_etl_udfs.enrichment.*`: external-I/O clients; hiện dùng `asyncio` + `urllib` từ Python standard library.
- `flink_etl_udfs.udfs.*`: imports `pyflink.table.udf`.
- `flink_etl_udfs.registry`: imports PyFlink types lazily/for registration.
- Current transforms do not import domain-heavy packages such as `pydicom`, `hl7apy`, `xarray`, `astropy`, `rapidfuzz` or parser clients.

## Requirements files

- `requirements.txt`: third-party packages that worker-side UDF/enrichment code actually imports. Hiện không có active runtime package ngoài PyFlink runtime do cluster cung cấp.
- `requirements-flink.txt`: pin `apache-flink==2.3.0` cho custom Python image/virtualenv cần tự bootstrap PyFlink.
- `requirements-dev.txt`: pytest, Ruff, Mypy và build tools.

Không nên đưa `apache-flink` vào per-job `--pyRequirements` nếu Flink distribution đã cung cấp matching PyFlink runtime.

## Build và submit

```bash
python -m pip install -r requirements-dev.txt
python -m build

./bin/flink run \
  --python your_job.py \
  --pyFiles dist/flink_etl_udfs-0.6.0-py3-none-any.whl \
  --pyRequirements requirements.txt
```

`--pyFiles` đưa wheel vào Python path của client và remote Python workers. `--pyRequirements` chỉ cài worker-side third-party dependencies khai báo trong `requirements.txt`.

## Async profile enrichment

`enrich_extract_profile_url` gọi external REST service, vì vậy TaskManager/Python worker phải route được tới endpoint. Endpoint mặc định có thể override bằng environment:

```bash
export FLINK_ETL_PROFILE_EXTRACT_ENDPOINT='http://profile-service:31263/api/scrap-command/v1/Scrap/ExtractSource'
export FLINK_ETL_PROFILE_EXTRACT_TIMEOUT_SECONDS='10'
```

Nếu dùng Kubernetes/Docker, set hai biến trên ở TaskManager container/environment chứ không chỉ ở máy submit job.

Flink 2.3 hỗ trợ asynchronous scalar functions cho external I/O. Nên cấu hình concurrency, timeout và retry theo tải của service thay vì tạo concurrency không giới hạn. Ví dụ trong TableEnvironment/job bootstrap:

```python
t_env.get_config().set("table.exec.async-scalar.max-concurrent-operations", "20")
t_env.get_config().set("table.exec.async-scalar.timeout", "15s")
t_env.get_config().set("table.exec.async-scalar.retry-strategy", "FIXED_DELAY")
t_env.get_config().set("table.exec.async-scalar.max-attempts", "3")
t_env.get_config().set("table.exec.async-scalar.retry-delay", "500ms")
```

Conservative defaults nên được benchmark với API thật. Nếu service có rate limit, concurrency phải thấp hơn capacity thực của backend.

## Custom Docker image / virtualenv

```bash
python -m pip install --upgrade pip setuptools
python -m pip install -r requirements-flink.txt
python -m pip install -r requirements.txt
python -m pip install --no-deps dist/flink_etl_udfs-0.6.0-py3-none-any.whl
```

Kiểm tra version:

```bash
python -c "import pyflink; print(pyflink.__version__)"
./bin/flink --version
```

PyFlink và cluster phải cùng release line; repository hiện target Flink `2.3.0`.

## Offline cluster

```bash
mkdir -p wheelhouse
python -m pip download -r requirements.txt -d wheelhouse

python -m pip install \
  --no-index \
  --find-links wheelhouse \
  -r requirements.txt
```

Lưu ý: offline pip cache không giải quyết network dependency của `enrich_*`; worker vẫn phải kết nối được tới enrichment service nội bộ.

## Pip dependency khác connector JAR

- Kafka SQL / Elasticsearch connector: Flink connector JAR/plugin.
- JDBC driver: Java JAR.
- Python package được import trực tiếp trong UDF: `requirements.txt`.
- `flink-etl-udfs`: wheel qua `--pyFiles` hoặc pre-install vào Python environment.
- REST lookup/enrichment: network route + async UDF configuration; không phải connector JAR.

## Khi thêm dependency mới

1. Pin package vào đúng requirements file.
2. Add tests cho code path sử dụng dependency.
3. Cập nhật `tests/test_dependencies.py` để import-to-pip mapping explicit.
4. Nếu package lớn hoặc parse file/model nặng, ưu tiên tách thành parser/enrichment service.
5. Nếu code gọi network/database/API, không đặt trong synchronous scalar UDF; dùng async UDF/Async I/O/lookup pattern và test bằng mock thay vì gọi service thật trong CI.

Dependency-contract test sẽ fail nếu source code thêm external import nhưng chưa khai báo cách cung cấp package cho cluster.
