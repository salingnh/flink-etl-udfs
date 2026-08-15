"""Export the curated public UDF catalog to Elasticsearch metadata JSON/NDJSON."""

from __future__ import annotations

import json
from pathlib import Path

from flink_etl_udfs.public_api import PUBLIC_FUNCTIONS

ARTIFACT_URI = "s3://fusion_center/transform-library/flink_etl_udfs.zip"
LIBRARY_VERSION = "0.7.1"

# Public SQL parameters. All are accepted from arbitrary SQL scalar types and
# internally TRY_CAST to STRING before the original transform logic runs.
PARAMS = {
    "etl_stable_record_id": ["source_system", "natural_key"],
    "osint_build_observation_id": ["source_url", "entity_key", "observed_at"],
    "itu_e164_normalize_phone": ["source_field", "default_country_code"],
    "icao9303_build_document_id": ["issuer_country", "document_number"],
    "iso18013_build_driving_licence_id": ["issuer_country", "issuer", "licence_number"],
    "iso18013_build_mdl_id": ["issuer", "document_identifier"],
    "iso23220_build_eid_id": ["issuer", "namespace", "document_id"],
    "oidc_build_subject_key": ["issuer", "subject_id"],
}

OUTPUTS = {
    "etl_is_valid_json": "BOOLEAN",
}

NONDETERMINISTIC = {"enrich_extract_profile_url"}

PARAM_LABELS = {
    "source_field": "Field",
    "source_system": "Source system",
    "natural_key": "Natural key",
    "source_url": "Source URL",
    "entity_key": "Entity key",
    "observed_at": "Observed at",
    "default_country_code": "Default country code",
    "issuer_country": "Issuer country",
    "document_number": "Document number",
    "issuer": "Issuer",
    "licence_number": "Licence number",
    "document_identifier": "Document identifier",
    "namespace": "Namespace",
    "document_id": "Document ID",
    "subject_id": "Subject ID",
}


def _description(name: str, standard: str | None, output: str, deterministic: bool) -> str:
    lines = ["### Mô tả", name, ""]
    if standard:
        lines.append(f"- **Standard:** {standard}")
    lines.extend(
        [
            "- **Input SQL type:** ANY scalar",
            "- **Internal cast:** STRING cho từng tham số public hiện tại",
            f"- **Output:** {output}",
            "- **Error policy:** TRY_CAST — cast/parse/format không hợp lệ trả `NULL`.",
        ]
    )
    if not deterministic:
        lines.append(
            "- **Runtime:** nondeterministic enrichment; lỗi hạ tầng/network vẫn được raise."
        )
    return "\n".join(lines)


def _config(params: list[str]) -> str:
    result = []
    for index, param in enumerate(params):
        result.append(
            {
                "param_key": param,
                "label": PARAM_LABELS.get(param, param.replace("_", " ").title()),
                "description": (
                    f"Input parameter `{param}`; accepts any SQL scalar and is internally "
                    "TRY_CAST to STRING."
                ),
                "type": "Text" if param == "default_country_code" else "Field",
                "is_primary": index == 0,
                "is_required": True,
                "sql_input_type": "ANY",
                "internal_cast_type": "STRING",
            }
        )
    return json.dumps(result, ensure_ascii=False, separators=(",", ":"))


def build_documents() -> list[dict]:
    docs = []
    for func_key, spec in PUBLIC_FUNCTIONS.items():
        params = PARAMS.get(func_key, ["source_field"])
        output = OUTPUTS.get(func_key, "STRING")
        deterministic = func_key not in NONDETERMINISTIC
        function_name = func_key.upper()
        placeholders = ", ".join("{{" + param + "}}" for param in params)

        docs.append(
            {
                "func_key": func_key,
                "name": spec["name"],
                "description": _description(
                    spec["name"], spec["standard"], output, deterministic
                ),
                "params": ",".join(params),
                "category": spec["category"],
                "standard": spec["standard"],
                "default_type": "ANY",
                "output": output,
                "pattern": f"{function_name}({placeholders})",
                "config": _config(params),
                "sql_position": "all",
                "allow_mapping": True,
                "status": 1,
                "type": "flink_sql",
                "error_policy": spec["error_policy"],
                "library": "flink-etl-udfs",
                "library_version": LIBRARY_VERSION,
                "implementation": {
                    "kind": "python_udf",
                    "function_name": function_name,
                    "entrypoint": spec["entrypoint"],
                    "artifact_uri": ARTIFACT_URI,
                    "input_types": ["ANY"] * len(params),
                    "internal_cast_types": ["STRING"] * len(params),
                    "result_type": output,
                    "deterministic": deterministic,
                },
            }
        )
    return docs


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "metadata"
    out_dir.mkdir(parents=True, exist_ok=True)

    docs = build_documents()
    if len(docs) != 66:
        raise RuntimeError(f"expected 66 public functions, got {len(docs)}")

    json_path = out_dir / "flink_transform_functions_elastic_v0.7.1.json"
    json_path.write_text(
        json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    bulk_path = out_dir / "flink_transform_functions_elastic_v0.7.1.bulk.ndjson"
    with bulk_path.open("w", encoding="utf-8") as handle:
        for doc in docs:
            handle.write(json.dumps({"index": {"_id": doc["func_key"]}}) + "\n")
            handle.write(json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "\n")

    print(json_path)
    print(bulk_path)


if __name__ == "__main__":
    main()
