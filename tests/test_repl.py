"""Тесты интерактивного цикла."""

import io
import unittest

from shell_emulator.cli import EXIT_OK, main
from shell_emulator.session import Session
from shell_emulator.repl import run_repl
from shell_emulator.shell import Shell

PROMPT = "> "


def run(text: str) -> str:
    """Запускает REPL на заданном вводе и возвращает вывод."""
    out = io.StringIO()
    run_repl(Shell(Session()), PROMPT, io.StringIO(text), out)
    return out.getvalue()


class ReplTest(unittest.TestCase):
    """Проверки диалога с пользователем."""

    def test_dialog(self):
        """Команды выполняются, после exit цикл завершается."""
        out = run("vfs-info\ncd /\nexit\nvfs-info\n")
        self.assertEqual(out, "> VFS: not loaded\n> > ")

    def test_error_message(self):
        """Ошибки выводятся в диалог и не прерывают работу."""
        out = run("foo\nexit 1\nexit\n")
        self.assertIn("foo: command not found\n", out)
        self.assertIn("exit: too many arguments\n", out)

    def test_eof(self):
        """Конец ввода завершает цикл."""
        self.assertEqual(run("vfs-info\n"), "> VFS: not loaded\n> \n")

    def test_empty_lines(self):
        """Пустые строки пропускаются."""
        self.assertEqual(run("\n\nexit\n"), "> > > ")


class MainTest(unittest.TestCase):
    """Проверки функции main."""

    def test_main_exit_code(self):
        """main возвращает EXIT_OK после exit."""
        out = io.StringIO()
        code = main([], io.StringIO("exit\n"), out)
        self.assertEqual(code, EXIT_OK)
        self.assertIn("$ ", out.getvalue())


if __name__ == "__main__":
    unittest.main()
