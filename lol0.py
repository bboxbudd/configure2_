import json
import os
import sys
from urllib.parse import urlparse

CONFIG_PATH = "config.json"

def load_config(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Конфигурационный файл '{path}' не найден.")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Ошибка синтаксиса JSON: {e}")

def validate_config(cfg):
    errors = []

    if not isinstance(cfg.get("package_name"), str) or not cfg["package_name"]:
        errors.append("Некорректное имя пакета (ожидается непустая строка).")

    repo = cfg.get("repository_path")
    if not isinstance(repo, str) or not repo:
        errors.append("Путь к репозиторию не задан.")
    else:
        parsed = urlparse(repo)
        if not (os.path.exists(repo) or parsed.scheme in ["http", "https"]):
            errors.append(f"'{repo}' не является существующим путём или допустимым URL.")

    if cfg.get("mode") not in ["local", "remote", "mock"]:
        errors.append("Поле 'mode' должно быть 'local', 'remote' или 'mock'.")

    if not isinstance(cfg.get("ascii_tree"), bool):
        errors.append("Параметр 'ascii_tree' должен быть true/false.")

    if "filter_substring" in cfg and not isinstance(cfg["filter_substring"], str):
        errors.append("Параметр 'filter_substring' должен быть строкой.")

    if errors:
        raise ValueError("\n".join(errors))

def main():
    try:
        cfg = load_config(CONFIG_PATH)
        validate_config(cfg)

        print("Конфигурация успешно загружена:\n")
        for key, value in cfg.items():
            print(f"{key} = {value}")

    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
