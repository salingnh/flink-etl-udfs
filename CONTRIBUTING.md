# Contributing

## Design rule

Mỗi transform reusable phải tách hai lớp:

1. `flink_etl_udfs.core.*`: pure Python transformation, deterministic khi có thể, unit-test độc lập.
2. `flink_etl_udfs.udfs.*`: thin PyFlink wrapper chỉ khai báo input/output type và determinism.

Không đặt network/database/API/file I/O trong scalar UDF. Dùng parser, lookup source, async enrichment, broadcast/reference data hoặc preprocessing cho các tác vụ đó.

## Curated public API

Trước khi thêm UDF, phải trả lời được ít nhất một câu hỏi sau bằng **có**:

- Transform có tái sử dụng rõ ràng giữa nhiều dataset/domain không?
- Transform có bám chuẩn/checksum/code system cụ thể không?
- Transform có semantics quốc gia/domain thật sự không thể thay bằng generic helper không?
- Transform có data-quality/provenance semantics đủ rõ để trở thành public API không?

Không tạo UDF mới chỉ để `trim`, `uppercase`, đổi tên vocabulary tùy ý hoặc vì một dataset có tên field riêng. **Không thêm compatibility/legacy alias.** Khi API phải đổi, version theo breaking change và xóa implementation cũ.

## Null và invalid-value policy

- Preserve `None` trừ khi contract nói rõ việc fill null.
- Normalizer không tự invent giá trị.
- Với invalid input, trả `None` khi contract là `value -> canonical value`; Boolean quality helper trả `False` theo contract.
- Không log plaintext sensitive values.

## Adding a function

1. Thêm pure transform dưới `core/`.
2. Thêm test cho `None`, empty, invalid, Unicode và boundary cases phù hợp.
3. Thêm thin PyFlink wrapper dưới `udfs/`.
4. Chỉ register SQL name sau khi tên và semantics đã được review là generic/standard/domain-correct.
5. Thêm comment mô tả ngay trước function và Python docstring.
6. Document tên hiển thị tiếng Việt, mức validation, before → after và SQL usage.
7. Nếu function phụ thuộc reference list thay đổi theo thời gian, không hard-code list: dùng lookup/reference data layer.

## Python dependency requirements

Nếu thêm third-party import dưới `src/`, cùng change phải khai báo cách package tới Flink runtime:

- `requirements.txt`: worker-side third-party libraries thực sự được UDF/core import;
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
