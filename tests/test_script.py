"""Тесты стартового скрипта и сквозные тесты main."""

import io
import os
import tempfile
import unittest
from pathlib import Path

from shell_emulator.cli import EXIT_OK, EXIT_SCRIPT_ERROR, main
from shell_emulator.session import Session
from shell_emulator.errors import EmulatorError
from shell_emulator.script import read_script, run_script
from shell_emulator.shell import Shell

PROMPT = "> "
ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "examples" / "scripts"


def run(lines):
    """Выполняет строки скрипта, возвращает (успех, вывод)."""
    out = io.StringIO()
    ok = run_script(Shell(Session()), lines, PROMPT, out)
    return ok, out.getvalue()


class RunScriptTest(unittest.TestCase):
    """Проверки run_script."""

    def test_echo_input_and_output(self):
        """На экране отображаются и ввод, и вывод."""
        ok, out = run(["vfs-info", "cd /"])
        self.assertTrue(ok)
        self.assertEqual(out, "> vfs-info\nVFS: not loaded\n> cd /\n")

    def test_stops_on_first_error(self):
        """Скрипт останавливается на первой ошибке."""
        ok, out = run(["ls", "foo", "cd never"])
        self.assertFalse(ok)
        self.assertEqual(out, "> ls\n> foo\nfoo: command not found\n")

    def test_comments_and_blank(self):
        """Пустые строки и комментарии пропускаются."""
        ok, out = run(["", "# note", "  ", "ls"])
        self.assertTrue(ok)
        self.assertEqual(out, "> ls\n")

    def test_exit_stops_script(self):
        """После exit остальные строки не выполняются."""
        ok, out = run(["exit", "ls"])
        self.assertTrue(ok)
        self.assertEqual(out, "> exit\n")


class ReadScriptTest(unittest.TestCase):
    """Проверки read_script."""

    def test_missing_file(self):
        """Отсутствующий файл — EmulatorError."""
        with self.assertRaises(EmulatorError):
            read_script("/no/such/script.emu")

    def test_reads_lines(self):
        """Строки читаются без символов перевода строки."""
        self.assertEqual(
            read_script(str(SCRIPTS / "basic.emu"))[1], "ls"
        )


class MainScriptTest(unittest.TestCase):
    """Сквозные проверки main со скриптом."""

    def call(self, argv, text=""):
        """Вызывает main, возвращает (код, вывод)."""
        out = io.StringIO()
        code = main(argv, io.StringIO(text), out)
        return code, out.getvalue()

    def test_debug_output(self):
        """При запуске выводятся все параметры."""
        code, out = self.call(["--prompt", "me>"], "exit\n")
        self.assertEqual(code, EXIT_OK)
        self.assertIn("[debug]   prompt = 'me>'", out)
        self.assertIn("[debug]   vfs    = (not set)", out)

    def test_custom_prompt(self):
        """Пользовательское приглашение используется в REPL."""
        _, out = self.call(["--prompt", "me>"], "vfs-info\nexit\n")
        self.assertIn("me> VFS: not loaded\n", out)

    def test_script_then_exit(self):
        """Скрипт с exit завершает работу без REPL."""
        script = str(SCRIPTS / "basic.emu")
        code, out = self.call(["--prompt", "$", "--script", script])
        self.assertEqual(code, EXIT_OK)
        self.assertIn("$ ls\n$ cd /\n$ cd\n", out)

    def test_script_error_code(self):
        """Ошибка в скрипте даёт код EXIT_SCRIPT_ERROR."""
        script = str(SCRIPTS / "stop_on_error.emu")
        code, out = self.call(["--script", script])
        self.assertEqual(code, EXIT_SCRIPT_ERROR)
        self.assertIn("foo: command not found", out)
        self.assertNotIn("never_printed", out.split("foo")[1])

    def test_missing_script(self):
        """Отсутствующий скрипт — сообщение и код ошибки."""
        code, out = self.call(["--script", "/no/such.emu"])
        self.assertEqual(code, EXIT_SCRIPT_ERROR)
        self.assertIn("cannot read script", out)

    def test_script_without_exit_goes_to_repl(self):
        """Скрипт без exit продолжается интерактивным режимом."""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "s.emu")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("ls\n")
            code, out = self.call(["--script", path], "vfs-info\nexit\n")
        self.assertEqual(code, EXIT_OK)
        self.assertIn("VFS: not loaded\n", out)


if __name__ == "__main__":
    unittest.main()
