from pathlib import Path
from typing import Any, List
import sys


def get_project_root() -> Path:
    return Path(__file__).parent


def str_to_int_list(s: str) -> List[int]:
    """
    cast the given comma separated string to an integer list
    :param s: string
    :return: integer list
    """

    return [int(number) for number in s.strip().split(',')]
    # try:
    #     return [int(number) for number in s.strip().split(',')]
    # except ValueError as e:
    #     return []


class Checks:
    """
    Provide type check for primitive types
    """

    @staticmethod
    def check_str(s: Any) -> bool:
        """
        Check if string is non-empty
        """
        return isinstance(s, str) and len(s.strip()) > 0

    @staticmethod
    def check_int(val: Any) -> bool:
        """check if val is integer and non negative"""
        return isinstance(val, int) and val >= 0


def log(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)
