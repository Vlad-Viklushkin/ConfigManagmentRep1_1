"""Тесты выполнения команд."""

import unittest

from shell_emulator.commands import Session
from shell_emulator.errors import CommandError
from shell_emulator.shell import Shell


class ShellTest(unittest.TestCase):
    """Проверки команд-заглушек, exit и обработки ошибок."""

    def __init__(self, *args, **kwargs):
        """Создаёт оболочку с новым сеансом."""
        super().__init__(*args, **kwargs)
        self.session = Session()
        self.shell = Shell(self.session)

    def test_ls_stub(self):
        """ls выводит своё имя и аргументы."""
        self.assertEqual(self.shell.execute("ls -l /tmp"), "ls -l /tmp")

    def test_ls_without_args(self):
        """ls без аргументов выводит только имя."""
        self.assertEqual(self.shell.execute("ls"), "ls")

    def test_cd_stub(self):
        """cd выводит своё имя и аргументы."""
        self.assertEqual(self.shell.execute("cd a b"), "cd a b")

    def test_empty_line(self):
        """Пустая строка не вызывает ошибок и ничего не выводит."""
        self.assertEqual(self.shell.execute("   "), "")

    def test_unknown_command(self):
        """Неизвестная команда вызывает CommandError."""
        with self.assertRaises(CommandError) as ctx:
            self.shell.execute("foo bar")
        self.assertEqual(str(ctx.exception), "foo: command not found")

    def test_exit(self):
        """exit останавливает сеанс."""
        self.assertEqual(self.shell.execute("exit"), "")
        self.assertFalse(self.session.running)

    def test_exit_with_args(self):
        """exit с аргументами — ошибка, сеанс продолжается."""
        with self.assertRaises(CommandError) as ctx:
            self.shell.execute("exit 1")
        self.assertEqual(str(ctx.exception), "exit: too many arguments")
        self.assertTrue(self.session.running)


if __name__ == "__main__":
    unittest.main()
