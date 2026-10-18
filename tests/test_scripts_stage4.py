"""Прогон стартовых скриптов этапа 4."""

import io
import unittest

from helpers import SCRIPTS, VFS_DIR
from shell_emulator.cli import EXIT_OK, EXIT_SCRIPT_ERROR, main


def call(script: str, vfs: str = "deep.xml"):
    """Запускает эмулятор со скриптом и VFS, возвращает (код, вывод)."""
    out = io.StringIO()
    argv = ["--vfs", str(VFS_DIR / vfs), "--prompt", "vfs>",
            "--script", str(SCRIPTS / script)]
    return main(argv, io.StringIO(), out), out.getvalue()


class Stage4ScriptsTest(unittest.TestCase):
    """Стартовые скрипты этапа 4."""

    def test_all_modes(self):
        """Скрипт со всеми режимами команд выполняется без ошибок."""
        code, out = call("stage4_commands.emu")
        self.assertEqual(code, EXIT_OK)
        self.assertIn("vfs> ls -la /home/user\n-       16 .profile\n", out)
        self.assertIn("6 directories, 3 files", out)
        self.assertIn("vfs> uname -a\n", out)

    def test_error_stops_script(self):
        """Ошибка в скрипте останавливает его."""
        code, out = call("stage4_error_end.emu")
        self.assertEqual(code, EXIT_SCRIPT_ERROR)
        self.assertIn("cd: /home/nobody: No such file or directory", out)
        self.assertNotIn("never_printed\n", out.split("nobody")[1])


if __name__ == "__main__":
    unittest.main()
