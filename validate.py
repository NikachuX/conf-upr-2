from urllib.parse import urlparse
import os
import argparse

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="DepViz — минимальный CLI-прототип для визуализации зависимостей (Этап 1)")

    p.add_argument("--package", "-p", required=True, help="Имя анализируемого пакета (обязательно)")
    p.add_argument("--repo", "-r", required=True, help="URL репозитория (режим real) или путь к файлу (режим test)")
    p.add_argument("--mode", "-m", choices=["real", "test"], default="real", help="Режим работы: real или test (по умолчанию: real)")
    p.add_argument("--version", "-v", default="latest", help="Версия пакета (например 1.0.0) или 'latest' (по умолчанию: latest)")
    p.add_argument("--ascii", "-a", action="store_true", help="Включить режим вывода зависимостей в формате ASCII-дерева")
    p.add_argument("--depth", "-d", type=int, default=0, help="Максимальная глубина анализа зависимостей")

    args = p.parse_args()
    return args


def is_url(s: str) -> bool:
    try:
        parsed = urlparse(s)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def validate_args(args: argparse.Namespace) -> None:
    # package
    if not args.package or args.package.strip() == "":
        raise ValueError("Параметр --package обязателен и не может быть пустым.")

    # mode
    if args.mode not in ("real", "test"):
        raise ValueError("Параметр --mode должен быть 'real' или 'test'.")

    # repo: if mode test -> expect a local path; if real -> expect URL
    if args.mode == "test":
        if not args.repo:
            raise ValueError("В тестовом режиме (--mode test) параметр --repo должен указывать путь к файлу тестового репозитория.")
        if not os.path.exists(args.repo):
            raise FileNotFoundError(f"Файл репозитория не найден: {args.repo}")
        if not os.path.isfile(args.repo):
            raise ValueError(f"Ожидался путь к файлу, а не к каталогу: {args.repo}")
    else:
        if not args.repo:
            raise ValueError("Параметр --repo обязателен и должен быть URL-адресом репозитория в режиме 'real'.")
        if not is_url(args.repo):
            raise ValueError("В режиме 'real' параметр --repo должен быть корректным URL (http/https).")

    if args.depth is not None:
        if args.depth < 0:
            raise ValueError("Параметр --depth должен быть целым числом >= 0 (0 = без лимита).")
