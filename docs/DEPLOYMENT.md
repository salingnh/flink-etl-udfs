# Deploying `flink-etl-udfs` to Apache Flink

## Dependency profile — 0.5.0

- `flink_etl_udfs.core.*`: Python standard library only.
- `flink_etl_udfs.udfs.*`: imports `pyflink.table.udf`.
- `flink_etl_udfs.registry`: imports PyFlink types lazily/for registration.
- Current scalar UDFs do not import domain-heavy packages such as `pydicom`, `hl7apy`, `xarray`, `astropy`, `rapidfuzz` or parser clients.

## Requirements files

- `requirements.txt`: third-party packages that worker-side UDF code actually imports. Hiện không có active runtime package ngoài PyFlink runtime do cluster cung cấp.
- `requirements-flink.txt`: pin `apache-flink==2.3.0` cho custom Python image/virtualenv cần tự bootstrap PyFlink.
- `requirements-dev.txt`: pytest, Ruff, Mypy và build tools.

Không nên đưa `apache-flink` vào per-job `--pyRequirements` nếu Flink distribution đã cung cấp matching PyFlink runtime.

## Build và submit

```bash
python -m pip install -r requirements-dev.txt
python -m build

./bin/flink run \
  --python your_job.py \
  --pyFiles dist/flink_etl_udfs-0.5.0-py3-none-any.whl \
  --pyRequirements requirements.txt
```

`--pyFiles` đưa wheel vào Python path của client và remote Python workers. `--pyRequirements` chỉ cài worker-side third-party dependencies khai báo trong `requirements.txt`.

## Custom Docker image / virtualenv

```bash
python -m pip install --upgrade pip setuptools
python -m pip install -r requirements-flink.txt
python -m pip install -r requirements.txt
python -m pip install --no-deps dist/flink_etl_udfs-0.5.0-py3-none-any.whl
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

## Pip dependency khác connector JAR

- Kafka SQL / Elasticsearch connector: Flink connector JAR/plugin.
- JDBC driver: Java JAR.
- Python package được import trực tiếp trong UDF: `requirements.txt`.
- `flink-etl-udfs`: wheel qua `--pyFiles` hoặc pre-install vào Python environment.

## Khi thêm dependency mới

1. Pin package vào đúng requirements file.
2. Add tests cho code path sử dụng dependency.
3. Cập nhật `tests/test_dependencies.py` để import-to-pip mapping explicit.
4. Nếu package lớn, parse file, gọi network hoặc cần model/reference data, ưu tiên tách thành parser/enrichment service thay vì cài trên mọi Python worker.

Dependency-contract test sẽ fail nếu source code thêm external import nhưng chưa khai báo cách cung cấp package cho cluster.
