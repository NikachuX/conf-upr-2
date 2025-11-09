import requests
import os


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

def get_deps_by_name(name, version):
    curr_version = version
    if version == "latest":
        response = requests.get(f"https://crates.io//api/v1/crates/{name}")
        if response.status_code == 200:
            data = response.json()
            crate = data.get('crate', [])
            curr_version = crate.get('max_version')
        else:
            print(f"Ошибка запроса: {response.status_code}")
            return
    url = f"https://crates.io/api/v1/crates/{name}/{curr_version}/dependencies"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        dependencies = data.get('dependencies', [])
        crate_ids = [dep.get('crate_id') for dep in dependencies if 'crate_id' in dep]
        return crate_ids
    else:
        print(f"Ошибка запроса: {response.status_code}")
        return


def parse_test_graph(path):
    graph = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            node, deps = line.strip().split(':')
            node = node.strip()
            deps = deps.strip().split() if deps.strip() else []
            graph[node] = deps
    return graph

def print_ascii_tree(graph, root, max_depth=10):
    stack = [(root, 0, [])]
    visited = set()

    while stack:
        node, depth, branches = stack.pop()
        prefix = ''
        for i, is_last in enumerate(branches[:-1]):
            prefix += '    ' if is_last else '│   '
        if depth > 0:
            prefix += '└── ' if branches and branches[-1] else '├── '

        print(prefix + node)

        if depth >= max_depth:
            continue
        if node in visited:
            print(prefix + "   (цикл)")
            continue
        visited.add(node)

        deps = graph.get(node, [])
        for i, dep in enumerate(reversed(deps)):  # reversed чтобы порядок был сверху вниз
            stack.append((dep, depth + 1, branches + [i == 0]))

def build_dependency_graph(root_name, version="latest", max_depth=3, test_mode=False, test_file=None):
    if test_mode:
        test_graph = parse_test_graph(test_file)
    else:
        test_graph = None

    graph = {}
    stack = [(root_name, 0)]
    visited = set()
    in_stack = set()

    while stack:
        package, depth = stack.pop()
        if package in visited:
            continue

        visited.add(package)
        in_stack.add(package)

        if depth >= max_depth:
            continue

        if test_mode:
            deps = test_graph.get(package, [])
        else:
            deps = get_deps_by_name(package, version) or []

        graph[package] = deps

        for dep in deps:
            if dep in in_stack:
                continue
            elif dep not in visited:
                stack.append((dep, depth + 1))

        in_stack.remove(package)

    return graph


def get_load_order(graph, root):
    visited = set()
    temp_mark = set()
    result = []

    def visit(node):
        if node in visited:
            return
        if node in temp_mark:
            raise RuntimeError(f"Циклическая зависимость обнаружена: {node}")
        temp_mark.add(node)
        for dep in graph.get(node, []):
            visit(dep)
        temp_mark.remove(node)
        visited.add(node)
        result.append(node)

    visit(root)
    return result[::-1]


