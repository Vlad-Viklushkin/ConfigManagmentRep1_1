"""Тесты параметров командной строки."""

import unittest

from shell_emulator.config import (
    NOT_SET, Config, format_debug, parse_args,
)


class ParseArgsTest(unittest.TestCase):
    """Проверки разбора параметров."""

    def test_defaults(self):
        """Без параметров все значения не заданы."""
        self.assertEqual(parse_args([]), Config())

    def test_all_params(self):
        """Все три параметра разбираются."""
        config = parse_args(
            ["--vfs", "a.xml", "--prompt", "$$", "--script", "s.emu"]
        )
        self.assertEqual(config.vfs_path, "a.xml")
        self.assertEqual(config.prompt, "$$")
        self.assertEqual(config.script_path, "s.emu")

    def test_unknown_param(self):
        """Неизвестный параметр приводит к завершению с ошибкой."""
        with self.assertRaises(SystemExit):
            parse_args(["--bogus"])


class FormatDebugTest(unittest.TestCase):
    """Проверки отладочного вывода."""

    def test_unset(self):
        """Не заданные параметры помечаются."""
        text = "\n".join(format_debug(Config()))
        self.assertEqual(text.count(NOT_SET), 3)

    def test_values(self):
        """Заданные значения присутствуют в выводе."""
        config = Config("v.xml", "my> ", "s.emu")
        text = "\n".join(format_debug(config))
        self.assertIn("'v.xml'", text)
        self.assertIn("'my> '", text)
        self.assertIn("'s.emu'", text)


if __name__ == "__main__":
    unittest.main()
