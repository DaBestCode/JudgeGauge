# JudgeGauge Schemas

## Compatibility Policy

The JudgeGauge JSON schemas adhere to the following versioning and compatibility policy:

* **Additive changes:** Adding new fields to a schema is allowed within the current version (e.g., within `v1`). Clients parsing the output must ignore unknown fields to maintain forward compatibility.
* **Breaking changes:** Removing existing fields, changing their data types, or altering their semantic meaning requires publishing an entirely new schema version (e.g., bumping to `v2`).
