from collections.abc import Iterable

StrOrList = str | Iterable[str]


def normalize_to_list(value: StrOrList) -> list[str]:
    """Accept str or iterable[str] and normalize to list[str]."""
    if isinstance(value, str):
        return [value]
    return list(value)
