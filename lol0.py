import json
import os
import sys
import gzip
import urllib.request
from urllib.parse import urlparse


CONFIG_PATH = "config.json"


# ==========================
# ЗАГРУЗКА КОНФИГА
# ==========================
def load_config(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Конфигурационный файл '{path}' не найден.")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Ошибка синтаксиса JSON: {e}")


# ==========================
# ЗАГРУЗКА ФАЙЛА PACKAGES
# ==========================
def load_packages_file(path):
    """Загружает и возвращает содержимое Packages (в виде строк)."""
    if path.startswith("http"):
        print(f"Скачивание {path} ...")
        response = urllib.request.urlopen(path)
        data = response.read()
        try:
            return gzip.decompress(data).decode("utf-8")
        except OSError:
            # если файл не сжат
            return data.decode("utf-8")
    elif path.endswith(".gz"):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return f.read()
    else:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()


# ==========================
# ПАРСИНГ ЗАВИСИМОСТЕЙ
# ==========================
def parse_dependencies(package_name, content):
    """Находит и возвращает список прямых зависимостей указанного пакета."""
    blocks = content.split("\n\n")
    for block in blocks:
        lines = block.split("\n")
        pkg = None
        depends = None
        for line in lines:
            if line.startswith("Package: "):
                pkg = line[len("Package: "):].strip()
            elif line.startswith("Depends: "):
                depends = line[len("Depends: "):].strip()
        if pkg == package_name:
            if not depends:
                return []
            deps = [d.split("(")[0].strip() for d in depends.split(",")]
            return deps
    raise ValueError(f"Пакет '{package_name}' не найден в репозитории.")


# ==========================
# ОСНОВНОЙ ВХОД
# ==========================
def main():
    try:
        cfg = load_config(CONFIG_PATH)

        package_name = cfg.get("package_name")
        repo_path = cfg.get("repository_path")
        filter_str = cfg.get("filter_substring", "")

        if not package_name or not repo_path:
            raise ValueError("Не указаны обязательные поля: 'package_name' и 'repository_path'.")

        print(f"Извлечение зависимостей для пакета '{package_name}'...")

        content = load_packages_file(repo_path)
        deps = parse_dependencies(package_name, content)

        # применим фильтр, если задан
        if filter_str:
            deps = [d for d in deps if filter_str in d]

        print(f"\nПрямые зависимости для '{package_name}':")
        if deps:
            for d in deps:
                print(f"  - {d}")
        else:
            print("  (нет зависимостей)")

    except Exception as e:
        print(f"\nОшибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()