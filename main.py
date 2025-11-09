import sys
from validate import validate_args, parse_args
from parsing import (build_dependency_graph, print_ascii_tree, get_load_order)
from visual import visualize_dependencies

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

    if kv['mode'] == 'real':
        root = kv['package']
        graph = build_dependency_graph(root, version=kv['version'], max_depth=kv['depth'])
    else:
        root = 'A'
        graph = build_dependency_graph(root, max_depth=kv['depth'], test_mode=True, test_file=kv['repo'])

    order = get_load_order(graph, root)
    print(" -> ".join(order))
    visualize_dependencies(graph, root)
    if kv['ascii'] == True:
        print_ascii_tree(graph, root, max_depth=kv['depth'])

if __name__ == '__main__':
    main()
