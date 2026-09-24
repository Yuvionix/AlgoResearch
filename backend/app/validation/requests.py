from __future__ import annotations

import re


_SYMBOL = re.compile(r"^[A-Za-z0-9^._-]{1,32}$")


def required_symbol(value: object, default: str = "NIFTY") -> str:
    symbol = str(value or default).strip()
    if not _SYMBOL.fullmatch(symbol):
        raise ValueError("Invalid symbol. Use 1-32 letters, numbers, dots, hyphens, or ^.")
    return symbol


def bounded_int(value: object, default: int, minimum: int, maximum: int, name: str) -> int:
    try:
        parsed = int(value if value not in (None, "") else default)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer.") from exc
    if not minimum <= parsed <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}.")
    return parsed


def positive_float(value: object, default: float, name: str) -> float:
    try:
        parsed = float(value if value not in (None, "") else default)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a number.") from exc
    if not parsed > 0:
        raise ValueError(f"{name} must be greater than zero.")
    return parsed