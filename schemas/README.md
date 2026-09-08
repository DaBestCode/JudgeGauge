# JudgeGauge JSON schemas

`judgegauge-result-v1.schema.json` defines the serialized JSON contract produced by JudgeGauge.

## Compatibility

Schema version `1` permits additive fields so integrations can safely ignore fields they do not know.
Removing a required field, changing a required field's meaning/type, or otherwise making a breaking
serialization change requires a new schema version. The Python `CalibrationResult` model remains
independent of this serialized version number.
