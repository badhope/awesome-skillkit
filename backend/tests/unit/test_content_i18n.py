"""
Unit tests for `app.core.content_i18n`.

These don't touch the DB or FastAPI — they exercise the locale-slicing
helper directly. The end-to-end test of the GET endpoints slicing
content lives in `tests/integration/test_skills_api.py`.
"""


from app.core.content_i18n import ALL_LOCALES, is_i18n_content, pick_translation


def test_is_i18n_content_false_for_flat_dict():
    assert is_i18n_content({"summary": "Hello"}) is False


def test_is_i18n_content_false_for_none():
    assert is_i18n_content(None) is False


def test_is_i18n_content_false_for_list():
    assert is_i18n_content([1, 2, 3]) is False


def test_is_i18n_content_true_for_localized_shape():
    content = {
        "default_locale": "en",
        "translations": {"en": {"summary": "Hello"}},
    }
    assert is_i18n_content(content) is True


def test_pick_translation_passes_through_flat_dict():
    flat = {"summary": "Hello"}
    assert pick_translation(flat, "en") == flat
    assert pick_translation(flat, "zh") == flat
    assert pick_translation(flat, "anything") == flat


def test_pick_translation_returns_requested_locale():
    i18n = {
        "default_locale": "en",
        "translations": {
            "en": {"summary": "Hello"},
            "zh": {"summary": "你好"},
        },
    }
    assert pick_translation(i18n, "en") == {"summary": "Hello"}
    assert pick_translation(i18n, "zh") == {"summary": "你好"}


def test_pick_translation_falls_back_to_default_locale():
    i18n = {
        "default_locale": "en",
        "translations": {
            "en": {"summary": "Hello"},
            "zh": {"summary": "你好"},
        },
    }
    # French was never translated → should fall back to the default.
    assert pick_translation(i18n, "fr") == {"summary": "Hello"}


def test_pick_translation_falls_back_to_first_when_default_missing():
    i18n = {
        "default_locale": "en",
        "translations": {
            "zh": {"summary": "你好"},
            "ja": {"summary": "こんにちは"},
        },
    }
    # default_locale='en' is missing → fall back to the first sorted
    # translation, which is 'ja' (deterministic).
    result = pick_translation(i18n, "en")
    assert result == {"summary": "こんにちは"}


def test_pick_translation_all_returns_full_object():
    i18n = {
        "default_locale": "en",
        "translations": {
            "en": {"summary": "Hello"},
            "zh": {"summary": "你好"},
        },
    }
    assert pick_translation(i18n, ALL_LOCALES) is i18n


def test_pick_translation_handles_none():
    assert pick_translation(None, "en") is None


def test_pick_translation_handles_list():
    assert pick_translation([1, 2, 3], "en") == [1, 2, 3]


def test_pick_translation_returns_empty_for_empty_translations():
    i18n = {"default_locale": "en", "translations": {}}
    assert pick_translation(i18n, "en") == {}
