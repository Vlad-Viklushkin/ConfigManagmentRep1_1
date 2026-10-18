"""Тесты команд ls и cd."""

import unittest

from helpers import make_shell
from shell_emulator.cmd_util import parse_options
from shell_emulator.errors import CommandError


class LsTest(unittest.TestCase):
    """Проверки ls."""

    def __init__(self, *args, **kwargs):
        """Оболочка с глубокой VFS."""
        super().__init__(*args, **kwargs)
        self.shell = make_shell()

    def run_ok(self, line):
        """Выполняет команду и возвращает вывод."""
        return self.shell.execute(line)

    def fail(self, line):
        """Выполняет команду, ожидая ошибку, возвращает её текст."""
        with self.assertRaises(CommandError) as ctx:
            self.shell.execute(line)
        return str(ctx.exception)

    def test_root(self):
        """ls без аргументов — содержимое корня по алфавиту."""
        self.assertEqual(self.run_ok("ls"), "etc\nhome\ntmp")

    def test_empty_dir(self):
        """Пустой каталог — пустой вывод."""
        self.assertEqual(self.run_ok("ls tmp"), "")

    def test_hidden(self):
        """Скрытые файлы видны только с -a."""
        self.assertEqual(self.run_ok("ls /home/user"), "docs")
        self.assertEqual(self.run_ok("ls -a /home/user"), ".profile\ndocs")

    def test_long(self):
        """-l показывает тип и размер."""
        out = self.run_ok("ls -l /home/user/docs")
        self.assertEqual(
            out, "d        0 archive\n-       16 report.txt"
        )

    def test_combined_flags(self):
        """Флаги объединяются: -la и -a -l."""
        expected = "-       16 .profile\nd        0 docs"
        self.assertEqual(self.run_ok("ls -la /home/user"), expected)
        self.assertEqual(self.run_ok("ls -a -l /home/user"), expected)

    def test_file(self):
        """ls для файла выводит его самого."""
        self.assertEqual(self.run_ok("ls /etc/hostname"), "/etc/hostname")
        self.assertEqual(
            self.run_ok("ls -l /etc/hostname"), "-        8 /etc/hostname"
        )

    def test_multiple_paths(self):
        """Несколько путей выводятся с заголовками."""
        out = self.run_ok("ls /etc /home")
        self.assertEqual(out, "/etc:\nhostname\n\n/home:\nuser")

    def test_relative_after_cd(self):
        """Относительные пути считаются от текущего каталога."""
        self.run_ok("cd home/user")
        self.assertEqual(self.run_ok("ls docs"), "archive\nreport.txt")
        self.assertEqual(self.run_ok("ls .."), "user")

    def test_errors(self):
        """Ошибки: нет пути, неверный флаг."""
        self.assertEqual(
            self.fail("ls /nope"),
            "ls: cannot access '/nope': No such file or directory",
        )
        self.assertEqual(self.fail("ls -z"), "ls: invalid option -- 'z'")
        self.assertIn("/etc/hostname/x", self.fail("ls /etc/hostname/x"))

    def test_error_in_second_path(self):
        """Ошибка в любом из путей прерывает команду."""
        self.fail("ls /etc /nope")


class CdTest(unittest.TestCase):
    """Проверки cd."""

    def __init__(self, *args, **kwargs):
        """Оболочка с глубокой VFS."""
        super().__init__(*args, **kwargs)
        self.shell = make_shell()
        self.session = self.shell.session

    def test_absolute_and_relative(self):
        """Абсолютный и относительный переход."""
        self.shell.execute("cd /home/user")
        self.assertEqual(self.session.cwd, "/home/user")
        self.shell.execute("cd docs/archive")
        self.assertEqual(self.session.cwd, "/home/user/docs/archive")

    def test_parent_and_dot(self):
        """`..` и `.`."""
        self.shell.execute("cd /home/user/docs")
        self.shell.execute("cd ../..")
        self.assertEqual(self.session.cwd, "/home")
        self.shell.execute("cd .")
        self.assertEqual(self.session.cwd, "/home")

    def test_no_args_goes_root(self):
        """cd без аргументов — в корень."""
        self.shell.execute("cd /etc")
        self.shell.execute("cd")
        self.assertEqual(self.session.cwd, "/")

    def test_above_root(self):
        """Выше корня не подняться."""
        self.shell.execute("cd ../..")
        self.assertEqual(self.session.cwd, "/")

    def test_errors_keep_cwd(self):
        """При ошибках текущий каталог не меняется."""
        self.shell.execute("cd /etc")
        messages = {
            "cd /nope": "cd: /nope: No such file or directory",
            "cd hostname": "cd: hostname: Not a directory",
            "cd a b": "cd: too many arguments",
        }
        for line, message in messages.items():
            with self.assertRaises(CommandError) as ctx:
                self.shell.execute(line)
            self.assertEqual(str(ctx.exception), message)
        self.assertEqual(self.session.cwd, "/etc")


class ParseOptionsTest(unittest.TestCase):
    """Проверки parse_options."""

    def test_flags_and_operands(self):
        """Флаги и операнды разделяются."""
        flags, rest = parse_options(["-al", "x", "-", "y"], "al", "ls")
        self.assertEqual(flags, {"a", "l"})
        self.assertEqual(rest, ["x", "-", "y"])

    def test_double_dash(self):
        """После -- всё считается операндами."""
        flags, rest = parse_options(["--", "-a"], "a", "ls")
        self.assertEqual(flags, set())
        self.assertEqual(rest, ["-a"])

    def test_invalid(self):
        """Недопустимый флаг."""
        with self.assertRaises(CommandError):
            parse_options(["-q"], "a", "ls")


if __name__ == "__main__":
    unittest.main()
