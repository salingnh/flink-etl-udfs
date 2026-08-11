# Deploying `flink-etl-udfs` to Apache Flink

## Dependency profile — 0.6.1

- `flink_etl_udfs.core.*`: Python standard library only.
- `flink_etl_udfs.enrichment.*`: external-I/O clients; hiện dùng `urllib` từ Python standard library.
- `flink_etl_udfs.udfs.*`: SQL-facing modules; chỉ import PyFlink và dependency thật sự cần cho chính module đó.
- `flink_etl_udfs.registry`: imports domain UDF modules lazily/for registration.
- Current transforms do not import domain-heavy packages such as `pydicom`, `hl7apy`, `xarray`, `astropy`, `rapidfuzz` or parser clients.

## Requirements files

- `requirements.txt`: third-party packages mà worker-side code import. Hiện không có active runtime package ngoài PyFlink runtime do cluster cung cấp.
- `requirements-flink.txt`: pin `apache-flink==2.2.1` cho custom Python image/virtualenv cần tự bootstrap PyFlink.
- `requirements-dev.txt`: pytest, Ruff, Mypy và build tools.

Không nên đưa `apache-flink` vào per-job `--pyRequirements` nếu Flink distribution đã cung cấp matching PyFlink runtime.

## Build artifact cho `python.files`

Đối với SQL Gateway, artifact ZIP phải có package `flink_etl_udfs/` ngay ở archive root. Repo có builder riêng để tránh tạo nhầm ZIP dạng `src/flink_etl_udfs/...`:

```bash
python scripts/build_python_files_zip.py
```

Output:

```text
dist/flink_etl_udfs.zip
└── flink_etl_udfs/
    ├── __init__.py
    ├── udfs/
    ├── enrichment/
    └── core/
```

Sau đó upload đúng file này lên object storage, ví dụ:

```text
s3://fusion_center/transform-library/flink_etl_udfs.zip
```

Flink thêm Python files/ZIP dependencies vào `PYTHONPATH`; vì vậy cấu trúc archive và fully-qualified module path phải khớp nhau.

## SQL Gateway registration

```sql
SET 'python.files' = 's3://fusion_center/transform-library/flink_etl_udfs.zip';

CREATE TEMPORARY SYSTEM FUNCTION VN_NORMALIZE_MOBILE_PHONE
AS 'flink_etl_udfs.udfs.vietnam.normalize_vn_mobile_phone'
LANGUAGE PYTHON;

CREATE TEMPORARY SYSTEM FUNCTION ENRICH_EXTRACT_PROFILE_URL
AS 'flink_etl_udfs.udfs.enrichment.extract_profile_url'
LANGUAGE PYTHON;
```

Hai entrypoint ưu tiên được cố ý giữ import graph nhỏ:

```text
flink_etl_udfs.udfs.vietnam
├── re / typing                 (stdlib)
└── pyflink.table.udf

flink_etl_udfs.udfs.enrichment
├── pyflink.table.udf
└── flink_etl_udfs.enrichment.profile
    ├── json / os / typing      (stdlib)
    └── urllib                  (stdlib)
```

`VN_NORMALIZE_MOBILE_PHONE` không import `research_domains`, finance, healthcare, geospatial hoặc các pack khác khi SQL Gateway resolve function.

## Synchronous profile enrichment

`enrich_extract_profile_url` gọi external REST service, vì vậy TaskManager/Python worker phải route được tới endpoint. Endpoint mặc định có thể override bằng environment:

```bash
export FLINK_ETL_PROFILE_EXTRACT_ENDPOINT='http://profile-service:31263/api/scrap-command/v1/Scrap/ExtractSource'
export FLINK_ETL_PROFILE_EXTRACT_TIMEOUT_SECONDS='10'
```

Nếu dùng Kubernetes/Docker, set hai biến trên ở TaskManager container/environment chứ không chỉ ở máy submit job.

Wrapper PyFlink của `enrich_extract_profile_url` là scalar UDF đồng bộ để tương thích Flink 2.2.1 SQL Gateway. Timeout nằm trong client qua `FLINK_ETL_PROFILE_EXTRACT_TIMEOUT_SECONDS`. Nếu service có rate limit, kiểm soát số request đồng thời bằng job parallelism, upstream filtering/batching, hoặc đưa enrichment sang service/lookup pattern riêng thay vì tăng song song không giới hạn trong SQL UDF.

## Wheel / Python job deployment

Nếu submit bằng Python job thay vì pure SQL Gateway:

```bash
python -m pip install -r requirements-dev.txt
python -m build

./bin/flink run \
  --python your_job.py \
  --pyFiles dist/flink_etl_udfs-0.6.1-py3-none-any.whl \
  --pyRequirements requirements.txt
```

## Custom Docker image / virtualenv

```bash
python -m pip install --upgrade pip setuptools
python -m pip install -r requirements-flink.txt
python -m pip install -r requirements.txt
python -m pip install --no-deps dist/flink_etl_udfs-0.6.1-py3-none-any.whl
```

Kiểm tra version:

```bash
python -c "import pyflink; print(pyflink.__version__)"
./bin/flink --version
```

PyFlink và cluster phải cùng release line; repository hiện target Flink `2.2.1`.

## Pre-deploy import smoke test

Trước khi upload artifact:

```bash
python scripts/build_python_files_zip.py

PYTHONPATH=dist/flink_etl_udfs.zip python -c \
  "from flink_etl_udfs.udfs.vietnam import normalize_vn_mobile_phone; print(normalize_vn_mobile_phone)"

PYTHONPATH=dist/flink_etl_udfs.zip python -c \
  "from flink_etl_udfs.udfs.enrichment import extract_profile_url; print(extract_profile_url)"
```

CI cũng kiểm tra ZIP có `flink_etl_udfs/__init__.py` tại archive root và resolve được hai SQL entrypoint từ artifact độc lập.

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
- `flink-etl-udfs`: ZIP/wheel qua `python.files` / `--pyFiles` hoặc pre-install vào Python environment.
- REST lookup/enrichment: network route + scalar UDF timeout/capacity control; không phải connector JAR.

## Khi thêm dependency mới

1. Với transform nhỏ chỉ dùng stdlib, ưu tiên implementation self-contained trong đúng module `udfs/*` để giảm import graph.
2. Chỉ tách helper/client khi logic đủ phức tạp, có I/O, hoặc thực sự được tái sử dụng.
3. Pin third-party package vào đúng requirements file ngay khi source import package đó.
4. Add tests cho code path sử dụng dependency và artifact import path.
5. Nếu package lớn hoặc parse file/model nặng, ưu tiên tách thành parser/enrichment service.
6. Nếu code gọi network/database/API trong scalar UDF, phải có timeout rõ ràng, `deterministic=False`, và mocked-I/O test thay vì gọi service thật trong CI. Với tải lớn, ưu tiên Async I/O/lookup pattern ngoài SQL UDF đồng bộ.

Dependency-contract test sẽ fail nếu source code thêm external import nhưng chưa khai báo cách cung cấp package cho cluster.
