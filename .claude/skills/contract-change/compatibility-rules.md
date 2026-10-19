# Compatibility rules (reference, loaded only when classifying)

| Change | Request side | Response side |
|---|---|---|
| Add optional field | additive | additive (clients must ignore unknown fields) |
| Add required field | **breaking** | additive |
| Remove field | additive if server ignores it | **breaking** |
| Rename field | **breaking** | **breaking** |
| Change type/format | **breaking** | **breaking** |
| Tighten validation (min/max/pattern) | **breaking** | additive |
| Loosen validation | additive | **breaking** if clients validate |
| Add enum value | additive | **breaking** unless consumers tolerate unknowns |
| Remove enum value | **breaking** | additive |
| New endpoint | additive | additive |
| Remove endpoint / change path or method | **breaking** | **breaking** |
| Change success status code | n/a | **breaking** |
| Add new error status code | n/a | additive if documented as possible |

In CI, `oasdiff breaking` classifies these automatically. Treat its ERR level as breaking.
