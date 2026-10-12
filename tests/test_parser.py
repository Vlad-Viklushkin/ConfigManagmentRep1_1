"""Тесты парсера строки ввода."""

import unittest

from shell_emulator.parser import parse_line


class ParseLineTest(unittest.TestCase):
    """Проверки разбора строки на команду и аргументы."""

    def test_empty_line(self):
        """Пустая строка даёт None."""
        self.assertIsNone(parse_line(""))

    def test_spaces_only(self):
        """Строка из пробелов даёт None."""
        self.assertIsNone(parse_line("   \t "))

    def test_command_only(self):
        """Команда без аргументов."""
        parsed = parse_line("ls")
        self.assertEqual(parsed.name, "ls")
        self.assertEqual(parsed.args, [])

    def test_command_with_args(self):
        """Команда с несколькими аргументами."""
        parsed = parse_line("cd /home user")
        self.assertEqual(parsed.name, "cd")
        self.assertEqual(parsed.args, ["/home", "user"])

    def test_extra_spaces(self):
        """Лишние пробелы между словами игнорируются."""
        parsed = parse_line("  ls   -l    dir  \n")
        self.assertEqual(parsed.name, "ls")
        self.assertEqual(parsed.args, ["-l", "dir"])


if __name__ == "__main__":
    unittest.main()
