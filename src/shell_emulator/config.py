"""Параметры командной строки и их отладочный вывод."""

import argparse
from dataclasses import dataclass
from typing import List, Optional

NOT_SET = "(not set)"


@dataclass(frozen=True)
class Config:
    """Настройки эмулятора, заданные пользователем."""

    vfs_path: Optional[str] = None
    prompt: Optional[str] = None
    script_path: Optional[str] = None


def build_parser() -> argparse.ArgumentParser:
    """Создаёт разборщик параметров командной строки."""
    parser = argparse.ArgumentParser(
        prog="shell_emulator",
        description="Эмулятор языка оболочки ОС (CLI).",
    )
    parser.add_argument(
        "--vfs", dest="vfs_path", metavar="PATH",
        help="путь к физическому расположению VFS",
    )
    parser.add_argument(
        "--prompt", dest="prompt", metavar="TEXT",
        help="пользовательское приглашение к вводу",
    )
    parser.add_argument(
        "--script", dest="script_path", metavar="PATH",
        help="путь к стартовому скрипту",
    )
    return parser


def parse_args(argv: Optional[List[str]] = None) -> Config:
    """Разбирает параметры командной строки в Config."""
    namespace = build_parser().parse_args(argv)
    return Config(
        vfs_path=namespace.vfs_path,
        prompt=namespace.prompt,
        script_path=namespace.script_path,
    )


def _show(value: Optional[str]) -> str:
    """Форматирует значение параметра для отладочного вывода."""
    return NOT_SET if value is None else repr(value)


def format_debug(config: Config) -> List[str]:
    """Возвращает строки отладочного вывода всех заданных параметров."""
    return [
        "[debug] Параметры запуска:",
        f"[debug]   vfs    = {_show(config.vfs_path)}",
        f"[debug]   prompt = {_show(config.prompt)}",
        f"[debug]   script = {_show(config.script_path)}",
    ]
