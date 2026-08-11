# Contributing

## Design rule

Transform reusable deterministic tách hai lớp:

1. `flink_etl_udfs.core.*`: pure Python transformation, deterministic khi có thể, unit-test độc lập.
2. `flink_etl_udfs.udfs.*`: thin PyFlink wrapper chỉ khai báo input/output type và determinism.

External I/O tách riêng:

1. `flink_etl_udfs.enrichment.*`: client/adapter gọi network/database/API, test bằng mock/fake response.
2. `flink_etl_udfs.udfs.*`: async PyFlink wrapper với `deterministic=False`.

Không đặt network/database/API/file I/O trong **synchronous scalar UDF**. Dùng parser, lookup source, async enrichment, Async I/O, broadcast/reference data hoặc preprocessing cho các tác vụ đó. Async enrichment phải có timeout, error policy và concurrency control rõ ràng.

## Curated public API

Trước khi thêm UDF, phải trả lời được ít nhất một câu hỏi sau bằng **có**:

- Transform có tái sử dụng rõ ràng giữa nhiều dataset/domain không?
- Transform có bám chuẩn/checksum/code system cụ thể không?
- Transform có semantics quốc gia/domain thật sự không thể thay bằng generic helper không?
- Transform có data-quality/provenance semantics đủ rõ để trở thành public API không?
- External lookup có contract ổn định và đủ giá trị để expose thành async enrichment không?

Không tạo UDF mới chỉ để `trim`, `uppercase`, đổi tên vocabulary tùy ý hoặc vì một dataset có tên field riêng. **Không thêm compatibility/legacy alias.** Khi API phải đổi, version theo breaking change và xóa implementation cũ.

## Null và invalid-value policy

- Preserve `None` trừ khi contract nói rõ việc fill null.
- Normalizer không tự invent giá trị.
- Với invalid input, trả `None` khi contract là `value -> canonical value`; Boolean quality helper trả `False` theo contract.
- External enrichment phân biệt invalid input với infrastructure failure: invalid input có thể trả `None`; HTTP/service/response lỗi nên raise để runtime retry/fail theo policy.
- Không log plaintext sensitive values.

## Adding a function

1. Thêm pure transform dưới `core/`, hoặc external client dưới `enrichment/` nếu có I/O.
2. Thêm test cho `None`, empty, invalid, Unicode và boundary cases phù hợp; external I/O phải mock, không gọi service thật trong CI.
3. Thêm thin PyFlink wrapper dưới `udfs/`; external I/O phải dùng async wrapper và `deterministic=False`.
4. Chỉ register SQL name sau khi tên và semantics đã được review là generic/standard/domain-correct.
5. Thêm comment mô tả ngay trước function và Python docstring.
6. Document tên hiển thị tiếng Việt, mức validation/enrichment, before → after và SQL usage.
7. Nếu function phụ thuộc reference list thay đổi theo thời gian, không hard-code list: dùng lookup/reference data layer. Chỉ hard-code migration table lịch sử đã đóng khi có nguồn chuẩn và test đầy đủ.

## Python dependency requirements

Nếu thêm third-party import dưới `src/`, cùng change phải khai báo cách package tới Flink runtime:

- `requirements.txt`: worker-side third-party libraries thực sự được UDF/core/enrichment import;
- `requirements-flink.txt`: pinned `apache-flink` cho custom Python image/virtualenv;
- `requirements-dev.txt`: test/lint/type-check/build tools.

Không đưa `apache-flink` vào worker `requirements.txt` chỉ vì wrapper import `pyflink`. Không cài parser dependency nặng lên mọi TaskManager nếu parsing chạy ở service/stage khác.

`tests/test_dependencies.py` fail khi có external import mới chưa được mapping tới pip provider.

## Documentation requirements

Public core transform phải có docstring nêu rõ:

- function canonicalize/validate gì;
- mức validation: syntax/checksum/reference-data;
- lossy behavior hoặc semantic limit quan trọng;
- hành vi với invalid input.

External enrichment client phải document:

- endpoint/config contract;
- request/response shape;
- timeout/error behavior;
- deterministic semantics;
- network requirement trên TaskManager/Python worker.

Registered SQL UDF phải có row trong `docs/functions/` gồm:

- tên hiển thị tiếng Việt;
- SQL function;
- chuẩn/phạm vi;
- mô tả;
- ví dụ giá trị trước → sau;
- `SELECT` usage example.

Khi thêm domain/data type/standard/dependency mới, cập nhật `docs/ETL_RESEARCH.md` và `docs/research/` nếu research scope thay đổi.

`tests/test_documentation.py` enforce:

1. mọi public core transform có docstring;
2. mọi registered SQL UDF có trong catalog;
3. mọi registered SQL UDF có before → after và `SELECT` usage example.

Xem `docs/DEPLOYMENT.md` cho cluster/custom-image/offline dependency patterns.
