"""Тесты формирования приглашения."""

import unittest
from unittest import mock

from shell_emulator import prompt


class DefaultPromptTest(unittest.TestCase):
    """Проверки приглашения по умолчанию."""

    def test_format(self):
        """Приглашение имеет вид username@hostname:~$ ."""
        with mock.patch.object(prompt, "get_username", return_value="bob"):
            with mock.patch.object(prompt, "get_hostname", return_value="pc"):
                self.assertEqual(prompt.default_prompt(), "bob@pc:~$ ")

    def test_username_fallback(self):
        """При ошибке getpass используется имя по умолчанию."""
        with mock.patch("getpass.getuser", side_effect=KeyError):
            self.assertEqual(prompt.get_username(), prompt.FALLBACK_USER)

    def test_hostname_fallback(self):
        """При пустом имени хоста используется значение по умолчанию."""
        with mock.patch("socket.gethostname", return_value=""):
            self.assertEqual(prompt.get_hostname(), prompt.FALLBACK_HOST)


if __name__ == "__main__":
    unittest.main()
