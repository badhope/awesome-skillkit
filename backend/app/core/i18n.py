"""Backend i18n.

Glue around stdlib `gettext`. Catalogs live in `app/locales/<lang>/LC_MESSAGES/`.
Compile them with `python -m app.core.i18n compile` (also wired as
`make i18n-compile`); CI runs `check` to fail on missing keys.
"""

from __future__ import annotations

import gettext
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, Iterator, List, Optional, Tuple

if TYPE_CHECKING:
    from fastapi import Request

# Lazy import so the CLI subcommands work before pydantic-settings is even
# installed (e.g. CI's i18n step before `pip install`).
def _get_settings():  # pragma: no cover - lazy import helper
    from app.core.config import get_settings
    return get_settings()


# Keep in sync with settings.SUPPORTED_LOCALES. First entry is the default
# and is always present, even if its .mo is missing.
_DEFAULT_LOCALES: Tuple[str, ...] = ("en", "zh")

# Anchored to the app/ dir so it works both under `poetry run` and in Docker.
_LOCALE_DIR = Path(__file__).resolve().parent.parent / "locales"

# Per-locale cache; GNUTranslations is safe to share across coroutines.
_translators: dict[str, gettext.GNUTranslations] = {}


def _supported_locales() -> List[str]:
    try:
        locales = _get_settings().SUPPORTED_LOCALES
    except Exception:
        locales = list(_DEFAULT_LOCALES)
    if not locales:
        locales = list(_DEFAULT_LOCALES)
    return list(locales)


def _default_locale() -> str:
    try:
        return _get_settings().DEFAULT_LOCALE
    except Exception:
        return _DEFAULT_LOCALES[0]


def _load_translator(locale: str) -> gettext.GNUTranslations:
    if locale in _translators:
        return _translators[locale]
    if not _LOCALE_DIR.exists():
        # No catalogs on disk — fall through to identity translations.
        translator: gettext.GNUTranslations = gettext.NullTranslations()
    else:
        translator = gettext.translation(
            domain="messages",
            localedir=str(_LOCALE_DIR),
            languages=[locale],
            fallback=True,
        )
    _translators[locale] = translator
    return translator


def _parse_accept_language(header: str, available: Iterable[str]) -> Optional[str]:
    """RFC 7231 §5.3.5 — return the highest-q available match, or None."""
    if not header:
        return None
    available_set = {a.lower() for a in available}
    candidates: list[tuple[float, str]] = []
    for chunk in header.split(","):
        parts = chunk.strip().split(";")
        if not parts:
            continue
        tag = parts[0].strip().lower().replace("_", "-")
        q = 1.0
        for param in parts[1:]:
            param = param.strip()
            if param.startswith("q="):
                try:
                    q = float(param[2:])
                except ValueError:
                    q = 1.0
        # `zh-CN` should still match our `zh` catalog. Add the primary
        # subtag with a slightly lower q so the exact match wins.
        candidates.append((q, tag))
        if "-" in tag:
            candidates.append((q * 0.99, tag.split("-", 1)[0]))
    candidates.sort(key=lambda x: -x[0])
    for _, tag in candidates:
        if tag in available_set:
            return tag
    return None


def resolve_locale(request: "Request") -> str:
    """Resolution order: ?lang= → X-Locale → Accept-Language → default."""
    supported = _supported_locales()
    default = _default_locale()

    q_lang = request.query_params.get("lang")
    if q_lang and q_lang.lower() in {s.lower() for s in supported}:
        return _normalize(q_lang, supported)

    x_locale = request.headers.get("X-Locale")
    if x_locale and x_locale.lower() in {s.lower() for s in supported}:
        return _normalize(x_locale, supported)

    accept = request.headers.get("Accept-Language", "")
    match = _parse_accept_language(accept, supported)
    if match:
        return match

    return default


def _normalize(locale: str, supported: Iterable[str]) -> str:
    target = locale.lower().replace("_", "-")
    for s in supported:
        if s.lower() == target:
            return s
        if "-" in s and s.lower().split("-", 1)[0] == target.split("-", 1)[0]:
            return s
    return locale


def gettext_for(locale: str) -> gettext.GNUTranslations:
    return _load_translator(locale)


@contextmanager
def use_locale(locale: str) -> Iterator[gettext.GNUTranslations]:
    """Install `locale`'s translator as the gettext module default for the
    duration of the block. Use from code paths that don't have a request
    (Celery tasks, CLI subcommands, startup hooks).
    """
    translator = _load_translator(locale)
    prev = gettext._default if hasattr(gettext, "_default") else None  # type: ignore[attr-defined]
    if hasattr(gettext, "_default"):
        gettext._default = translator  # type: ignore[attr-defined]
    try:
        yield translator
    finally:
        if prev is not None and hasattr(gettext, "_default"):
            gettext._default = prev  # type: ignore[attr-defined]


def _(message: str, locale: str, **params: object) -> str:
    """Translate `message` for `locale`, interpolating `params` with str.format.

    Missing key → English source. Bad placeholder → still returns the
    translation (we don't want to raise from inside a handler).
    """
    translated = _load_translator(locale).gettext(message)
    if params:
        try:
            translated = translated.format(**params)
        except (KeyError, IndexError):
            pass
    return translated


def localized_http_exception(
    request: "Request",
    status_code: int,
    message: str,
    *,
    extra_headers: Optional[dict[str, str]] = None,
    **params: object,
):
    """Build an HTTPException whose `detail` is translated for the request's
    locale, and stamp a Content-Language header on it.

    Example:
        raise localized_http_exception(request, 404, "Skill not found.")
        raise localized_http_exception(
            request, 429, "Rate limit exceeded. Try again in {seconds} s.",
            seconds=retry_after,
            extra_headers={"Retry-After": str(retry_after)},
        )
    """
    from fastapi import HTTPException

    locale = getattr(request.state, "locale", _default_locale())
    detail = _(message, locale, **params)
    headers: dict[str, str] = {"Content-Language": locale}
    if extra_headers:
        headers.update(extra_headers)
    return HTTPException(status_code=status_code, detail=detail, headers=headers)


# ----------------------------------------------------------------------
# Catalog compilation
# ----------------------------------------------------------------------


def compile_catalogs() -> int:
    """Compile every .po under _LOCALE_DIR into a .mo using GNU `msgfmt`.

    We don't roll our own MO encoder: the format has a couple of
    sharp edges (string ordering, hash table layout, header entry
    shape) and the stdlib validates strictly. msgfmt is in
    `apt-get install gettext` / `brew install gettext` / `apk add gettext-dev`.
    """
    import shutil
    import subprocess

    if not shutil.which("msgfmt"):
        raise RuntimeError(
            "GNU `msgfmt` is required to compile .po catalogs but was not "
            "found on PATH. Install it with `apt-get install gettext` "
            "(Debian/Ubuntu), `brew install gettext` (macOS), or "
            "`apk add gettext-dev` (Alpine)."
        )

    compiled = 0
    for po in _LOCALE_DIR.rglob("*.po"):
        mo = po.with_suffix(".mo")
        subprocess.check_call(
            ["msgfmt", "-o", str(mo), str(po)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        compiled += 1
    return compiled


def _read_po(path: Path) -> list[tuple[str, str]]:
    """Tiny .po parser — just enough to do `check` from the stdlib."""
    entries: list[tuple[str, str]] = []
    msgid: list[str] = []
    msgstr: list[str] = []
    state: str | None = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            stripped = line.strip()
            if not stripped:
                if msgid or msgstr:
                    entries.append(("".join(msgid), "".join(msgstr)))
                    msgid, msgstr, state = [], [], None
                continue
            if stripped.startswith("#"):
                continue
            if stripped.startswith("msgid "):
                msgid = [_unquote(stripped[len("msgid ") :])]
                state = "msgid"
            elif stripped.startswith("msgstr "):
                msgstr = [_unquote(stripped[len("msgstr ") :])]
                state = "msgstr"
            elif stripped.startswith('"'):
                chunk = _unquote(stripped)
                if state == "msgid":
                    msgid.append(chunk)
                elif state == "msgstr":
                    msgstr.append(chunk)
    if msgid or msgstr:
        entries.append(("".join(msgid), "".join(msgstr)))
    return entries


def _unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
    out: list[str] = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            nxt = s[i + 1]
            mapping = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}
            out.append(mapping.get(nxt, nxt))
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def check_catalogs() -> int:
    """Every key in the default locale must be present in the others.

    Returns the number of consistent keys; exits non-zero on mismatch.
    """
    import sys

    catalogs: dict[str, set[str]] = {}
    for po in _LOCALE_DIR.rglob("*.po"):
        locale = po.parts[-3]  # .../locales/<lang>/LC_MESSAGES/messages.po
        keys = {k for k, _ in _read_po(po) if k}
        catalogs[locale] = keys

    if not catalogs:
        print("No catalogs found", file=sys.stderr)
        return 0

    default_locale = _default_locale()
    if default_locale not in catalogs:
        print(f"Default locale {default_locale!r} has no catalog", file=sys.stderr)
        sys.exit(1)

    reference = catalogs[default_locale]
    failed = 0
    for locale, keys in catalogs.items():
        missing = reference - keys
        if missing:
            failed += 1
            print(
                f"  [{locale}] missing {len(missing)} key(s):",
                file=sys.stderr,
            )
            for k in sorted(missing):
                print(f"    {k!r}", file=sys.stderr)

    if failed:
        print(
            f"i18n check FAILED: {failed} locale(s) have missing keys",
            file=sys.stderr,
        )
        sys.exit(1)
    return len(reference)


if __name__ == "__main__":  # pragma: no cover
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "compile":
        n = compile_catalogs()
        print(f"Compiled {n} catalog(s) into {_LOCALE_DIR}")
    elif len(sys.argv) > 1 and sys.argv[1] == "check":
        n = check_catalogs()
        print(f"i18n check passed: {n} key(s) consistent across locales")
    else:
        print(__doc__)
