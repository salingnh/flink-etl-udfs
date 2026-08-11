# External enrichment / REST lookup

Đăng ký bằng `register_enrichment_udfs(t_env)` hoặc trực tiếp từ SQL bằng fully-qualified Python entrypoint.

Nhóm `enrich_*` dành cho transform có I/O ra hệ thống ngoài. `enrich_extract_profile_url` hiện dùng **synchronous general scalar UDF** (`udf(...)`) để tương thích ổn định với Flink SQL Gateway 2.2.x. Hàm vẫn được khai báo `deterministic=False` vì kết quả phụ thuộc dịch vụ ngoài.

| Tên hiển thị | SQL function | Phạm vi | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Trích thông tin URL profile | `enrich_extract_profile_url` | Sync REST enrichment | Nhận một URL profile HTTP(S), gọi `ExtractSource` với `parse_only=false`, `parse_display_name=false`, rồi trả phần tử đầu tiên trong `result` dưới dạng compact JSON. URL rỗng/sai trả `NULL`; lỗi transport/service raise exception. | `https://facebook.com/sangnv` → `{"actor_id":"100001614198876","actor_username":"sangnv",...,"platform":"facebook"}` | `SELECT enrich_extract_profile_url(profile_url) FROM profile_source;` |

## Python entrypoint

Artifact phải làm cho package `flink_etl_udfs` import được trong Python worker. Entry point SQL là:

```text
flink_etl_udfs.udfs.enrichment.extract_profile_url
```

Object trên được tạo trực tiếp ở module load bằng:

```python
extract_profile_url = udf(
    extract_profile_url_sync,
    input_types=["STRING"],
    result_type="STRING",
    deterministic=False,
)
```

Không dùng coroutine/factory trung gian cho entrypoint này.

## API contract mặc định

Endpoint mặc định:

```text
http://10.9.3.70:31263/api/scrap-command/v1/Scrap/ExtractSource
```

Request body:

```json
{
  "parse_only": false,
  "parse_display_name": false,
  "sources": ["https://facebook.com/sangnv"]
}
```

Headers:

```text
Accept: text/plain
Content-Type: application/json-patch+json
```

UDF chỉ trả object đầu tiên trong `result`, ví dụ:

```json
{
  "actor_id": "100001614198876",
  "actor_username": "sangnv",
  "domain": "facebook.com",
  "is_social": true,
  "platform": "facebook",
  "platform_alias": "facebook.com",
  "source_type": 1,
  "type": "user",
  "url": "https://facebook.com/sangnv"
}
```

## Cấu hình cluster

Có thể override endpoint mà không cần build lại artifact:

```bash
export FLINK_ETL_PROFILE_EXTRACT_ENDPOINT='http://profile-service:31263/api/scrap-command/v1/Scrap/ExtractSource'
export FLINK_ETL_PROFILE_EXTRACT_TIMEOUT_SECONDS='10'
```

Các biến môi trường phải có mặt trong Python worker/TaskManager environment.

## SQL usage

```sql
SET 'python.files' = 's3://fusion_center/transform-library/flink_etl_udfs.zip';

CREATE TEMPORARY SYSTEM FUNCTION ENRICH_EXTRACT_PROFILE_URL
AS 'flink_etl_udfs.udfs.enrichment.extract_profile_url'
LANGUAGE PYTHON;

SELECT
    profile_url,
    ENRICH_EXTRACT_PROFILE_URL(profile_url) AS profile_source_json
FROM profile_source;
```

Nếu cần lấy từng field từ JSON output, có thể dùng JSON functions của Flink SQL ở bước tiếp theo:

```sql
WITH enriched AS (
    SELECT
        profile_url,
        ENRICH_EXTRACT_PROFILE_URL(profile_url) AS profile_source_json
    FROM profile_source
)
SELECT
    profile_url,
    JSON_VALUE(profile_source_json, '$.actor_id') AS actor_id,
    JSON_VALUE(profile_source_json, '$.actor_username') AS actor_username,
    JSON_VALUE(profile_source_json, '$.platform') AS platform,
    JSON_VALUE(profile_source_json, '$.domain') AS domain
FROM enriched;
```

Do đây là synchronous network call, throughput của operator phụ thuộc latency của API. Khi API đã ổn định và runtime được chuẩn hóa, có thể tách enrichment sang lookup/async operator riêng ở bước sau.
