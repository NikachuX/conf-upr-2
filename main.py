import sys
from validate import is_url, validate_args, parse_args


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

    for k, v in kv.items():
        print(f"{k} = {v}")


if __name__ == '__main__':
    main()
