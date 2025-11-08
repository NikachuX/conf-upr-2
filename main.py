import sys
from validate import validate_args, parse_args
from parsing import get_toml, get_deps_by_name, build_dependency_graph, print_ascii_tree


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

    graph = build_dependency_graph(kv["package"], max_depth=2)
    print("\nГраф зависимостей\n")
    print_ascii_tree(graph, kv["package"])

if __name__ == '__main__':
    main()
