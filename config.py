import argparse
import yaml
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Эмулятор оболочки ОС")
    parser.add_argument('--vfs', help='Путь к VFS (JSON)')
    parser.add_argument('--script', help='Путь к стартовому скрипту')
    parser.add_argument('--config', help='Путь к YAML-конфигу')
    return parser.parse_args()


def load_config(args):
    params = {'vfs': args.vfs, 'script': args.script}

    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f) or {}
            if 'vfs_path' in cfg:
                params['vfs'] = cfg['vfs_path']
            if 'script_path' in cfg:
                params['script'] = cfg['script_path']
        except FileNotFoundError:
            print(f"Ошибка: конфиг не найден: {args.config}", file=sys.stderr)
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Ошибка YAML: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Ошибка чтения конфига: {e}", file=sys.stderr)
            sys.exit(1)

    print("Параметры запуска:")
    print(f"  VFS:    {params['vfs']}")
    print(f"  Script: {params['script']}")
    return params