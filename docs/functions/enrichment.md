# External enrichment / REST lookup

Đăng ký bằng `register_enrichment_udfs(t_env)`.

Nhóm `enrich_*` dành cho transform có I/O ra hệ thống ngoài. Khác với scalar UDF deterministic, các hàm này là nondeterministic, phải có timeout rõ ràng, và chỉ nên bật khi Python worker/TaskManager route được tới service.

| Tên hiển thị | SQL function | Phạm vi | Mô tả | Giá trị trước → sau | Ví dụ SQL |
| --- | --- | --- | --- | --- | --- |
| Trích thông tin URL profile | `enrich_extract_profile_url` | Synchronous REST enrichment | Nhận một URL profile HTTP(S), gọi `ExtractSource` với `parse_only=false`, `parse_display_name=false`, rồi trả phần tử đầu tiên trong `result` dưới dạng compact JSON. URL rỗng/sai trả `NULL`; lỗi transport/service raise exception thay vì âm thầm biến outage thành missing data. Wrapper là scalar UDF đồng bộ để tương thích Flink 2.2.1 SQL Gateway. | `https://facebook.com/sangnv` → `{"actor_id":"100001614198876","actor_username":"sangnv",...,"platform":"facebook"}` | `SELECT enrich_extract_profile_url(profile_url) FROM profile_source;` |

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

Có thể override endpoint mà không cần build lại wheel:

```bash
export FLINK_ETL_PROFILE_EXTRACT_ENDPOINT='http://profile-service:31263/api/scrap-command/v1/Scrap/ExtractSource'
export FLINK_ETL_PROFILE_EXTRACT_TIMEOUT_SECONDS='10'
```

Các biến môi trường phải có mặt trong Python worker/TaskManager environment.

## SQL usage

```sql
SELECT
    profile_url,
    enrich_extract_profile_url(profile_url) AS profile_source_json
FROM profile_source;
```

Nếu cần lấy từng field từ JSON output, có thể dùng JSON functions của Flink SQL ở bước tiếp theo, ví dụ:

```sql
WITH enriched AS (
    SELECT
        profile_url,
        enrich_extract_profile_url(profile_url) AS profile_source_json
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

`enrich_extract_profile_url` được khai báo `deterministic=False`. Không dùng function này trong khóa ID deterministic hoặc giả định cùng URL luôn trả cùng một kết quả theo thời gian.
