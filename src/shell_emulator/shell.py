"""Ядро эмулятора: выполнение одной строки ввода."""

from shell_emulator.commands import COMMANDS, Session
from shell_emulator.errors import CommandError
from shell_emulator.parser import parse_line


class Shell:
    """Выполняет команды в рамках одного сеанса."""

    def __init__(self, session: Session) -> None:
        """Создаёт оболочку, привязанную к сеансу."""
        self.session = session

    def execute(self, line: str) -> str:
        """Выполняет строку и возвращает текст вывода.

        Пустая строка ничего не делает. Для неизвестной команды
        и неверных аргументов бросает CommandError.
        """
        parsed = parse_line(line)
        if parsed is None:
            return ""
        handler = COMMANDS.get(parsed.name)
        if handler is None:
            raise CommandError(f"{parsed.name}: command not found")
        return handler(self.session, parsed.args)
