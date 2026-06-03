"""Locale-aware slicing for `Skill.content` JSONB.

Authors can store translatable content in two shapes:

1. Flat (legacy): a single dict, returned as-is for every locale.
2. Localized: `{"default_locale": "en", "translations": {"en": {...}, "zh": {...}}}`.

`pick_translation` returns the slice for the requested locale, falling back
to `default_locale` and then to "any translation we have". `is_i18n_content`
short-circuits the slicing for flat dicts.
"""

from __future__ import annotations

from typing import Any

# Pass as the `locale` arg to get the full translations map unchanged.
# (Used by the editing UI.)
ALL_LOCALES = "all"


def escape_like(s: str) -> str:
    """Escape SQL `LIKE` / `ILIKE` wildcards in user-supplied search
    strings so a literal `%` or `_` in the query doesn't turn into a
    wildcard match.

    Pair this with `Column.ilike(f"%{escape_like(q)}%", escape="\\\\")`
    (or the bare Python `\\\\` written as `escape="\\"` in source) so
    the DB knows the backslash is the escape character. PostgreSQL
    and SQLite both honour the explicit `ESCAPE` clause.
    """
    return s.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def is_i18n_content(content: Any) -> bool:
    return (
        isinstance(content, dict)
        and "translations" in content
        and isinstance(content["translations"], dict)
        and "default_locale" in content
    )


def pick_translation(content: Any, locale: str) -> Any:
    # Not in the i18n shape — return as-is.
    if not is_i18n_content(content):
        return content

    translations: dict[str, Any] = content.get("translations", {}) or {}
    default_locale: str = content.get("default_locale", "")

    if locale == ALL_LOCALES:
        return content

    if locale in translations:
        return translations[locale]

    if default_locale and default_locale in translations:
        return translations[default_locale]

    if translations:
        # Last-resort: anything we have. Sorted for determinism.
        return translations[sorted(translations.keys())[0]]

    return {}

