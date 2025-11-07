import sys
import os
from validate import validate_args, parse_args
import requests

def parse_cargo_toml(path):
    deps = []
    in_deps_section = False
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if line.startswith('[dependencies]'):
                    in_deps_section = True
                    continue
                if line.startswith('[') and not line.startswith('[dependencies]'):
                    in_deps_section = False
                if in_deps_section and '=' in line:
                    key, value = line.split('=', 1)
                    deps.append(key)
    except Exception as e:
        raise RuntimeError(f"Ошибка при чтении Cargo.toml: {e}")
    return deps

def get_toml(url):
    response = requests.get(url)
    content = response.text
    with open('dep.toml', 'w', encoding='utf-8') as f:
        f.write(content)
    deps = parse_cargo_toml("dep.toml")
    os.remove("dep.toml")
    return deps


def main():
    try:
        args = parse_args()
        validate_args(args)
    except FileNotFoundError as e:
        print(f"ОШИБКА: {e}", file=sys.stderr)
        sys.exit(2)
    except ValueError as e:
        print(f"Неверные параметры: {e}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"Неожиданная ошибка при разборе параметров: {e}", file=sys.stderr)
        sys.exit(4)

    kv = {
        "package": args.package,
        "repo": args.repo,
        "mode": args.mode,
        "version": args.version,
        "ascii": args.ascii,
        "depth": args.depth,
    }

    deps = get_toml(kv['repo'])
    print(deps)

if __name__ == '__main__':
    main()
