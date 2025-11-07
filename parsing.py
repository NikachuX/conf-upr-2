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