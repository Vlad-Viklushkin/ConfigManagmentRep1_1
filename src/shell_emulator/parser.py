"""Простой парсер строки ввода."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class ParsedLine:
    """Результат разбора строки: имя команды и список аргументов."""

    name: str
    args: List[str] = field(default_factory=list)


def parse_line(line: str) -> Optional[ParsedLine]:
    """Разделяет строку на команду и аргументы по пробелам.

    Возвращает None, если строка пустая или состоит из пробелов.
    """
    parts = line.split()
    if not parts:
        return None
    return ParsedLine(parts[0], parts[1:])
