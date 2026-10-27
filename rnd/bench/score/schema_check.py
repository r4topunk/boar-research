"""Minimal JSON Schema (draft 2020-12 subset) validator, stdlib only (jsonschema is not installed here).

Supports what rnd/bench/device/device-metrics.schema.json uses: type (incl. lists, integer vs number, null),
required, properties, additionalProperties: false, enum, const, pattern, items, minimum, $ref to #/$defs/*.
`format` is ignored (annotation only in 2020-12)."""
import re

_TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def validate(value, schema, root=None, path="$"):
    """Returns a list of error strings (empty = valid)."""
    root = root if root is not None else schema
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            return [f"{path}: unsupported $ref {ref}"]
        target = root
        for part in ref[2:].split("/"):
            target = target[part]
        schema = {**target, **{k: v for k, v in schema.items() if k not in ("$ref", "description")}}
    errs = []
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_TYPES[t](value) for t in types):
            return [f"{path}: expected {'|'.join(types)}, got {type(value).__name__}"]
    if "const" in schema and value != schema["const"]:
        errs.append(f"{path}: must be {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errs.append(f"{path}: {value!r} not in {schema['enum']}")
    if isinstance(value, str) and "pattern" in schema and not re.search(schema["pattern"], value):
        errs.append(f"{path}: {value!r} does not match {schema['pattern']}")
    if _TYPES["number"](value) and "minimum" in schema and value < schema["minimum"]:
        errs.append(f"{path}: {value} < minimum {schema['minimum']}")
    if isinstance(value, dict):
        props = schema.get("properties", {})
        for k in schema.get("required", []):
            if k not in value:
                errs.append(f"{path}: missing required '{k}'")
        for k, v in value.items():
            if k in props:
                errs += validate(v, props[k], root, f"{path}.{k}")
            elif schema.get("additionalProperties") is False:
                errs.append(f"{path}: unexpected property '{k}'")
    if isinstance(value, list) and "items" in schema:
        for i, v in enumerate(value):
            errs += validate(v, schema["items"], root, f"{path}[{i}]")
    return errs
