"""Write registry/series/<id>.yaml files from compact specs (keeps yaml layout uniform).

    python scripts/new_series.py specs.yaml   # a list of partial series dicts
Fields not given are filled from registry/series/_template.yaml. Existing files are never overwritten.
"""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in over.items():
        out[k] = deep_merge(base[k], v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return out


def main() -> None:
    template = yaml.safe_load((ROOT / "registry/series/_template.yaml").read_text())
    for spec in yaml.safe_load(Path(sys.argv[1]).read_text()):
        path = ROOT / "registry/series" / f"{spec['id']}.yaml"
        if path.exists():
            print(f"exists, skipped: {path.relative_to(ROOT)}")
            continue
        path.write_text(yaml.safe_dump(deep_merge(template, spec), sort_keys=False, allow_unicode=True))
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
