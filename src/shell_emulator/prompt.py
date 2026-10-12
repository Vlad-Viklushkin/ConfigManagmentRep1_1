"""Формирование приглашения к вводу на основе данных реальной ОС."""

import getpass
import socket
from typing import Optional

FALLBACK_USER = "user"
FALLBACK_HOST = "localhost"
HOME_DIR_MARK = "~"
PROMPT_SUFFIX = "$"


def get_username() -> str:
    """Возвращает имя текущего пользователя ОС."""
    try:
        return getpass.getuser()
    except (KeyError, OSError):
        return FALLBACK_USER


def get_hostname() -> str:
    """Возвращает имя хоста ОС."""
    return socket.gethostname() or FALLBACK_HOST


def default_prompt() -> str:
    """Возвращает приглашение вида `username@hostname:~$ `."""
    user = get_username()
    host = get_hostname()
    return f"{user}@{host}:{HOME_DIR_MARK}{PROMPT_SUFFIX} "


def resolve_prompt(custom: Optional[str]) -> str:
    """Возвращает итоговое приглашение.

    Пользовательское приглашение дополняется пробелом, если оно
    не заканчивается пробельным символом. Без него — приглашение ОС.
    """
    if custom is None:
        return default_prompt()
    if custom and not custom[-1].isspace():
        return custom + " "
    return custom
