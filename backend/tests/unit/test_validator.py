import pytest

from app.services.skill_validator import SkillValidator, ValidationResult, LintResult


class TestSkillValidator:

    def setup_method(self) -> None:
        self.validator = SkillValidator()

    def test_valid_skill_structure(self) -> None:
        content = """---
name: "Test Skill"
description: "A comprehensive test skill for code generation"
category: "code_generation"
version: "1.0.0"
author: "Test Author"
tags:
  - python
  - testing
license: "MIT"
---

# Test Skill

## Usage

This skill can be used to generate test code.

## Examples

```python
print("Hello World")
```

## Installation

```bash
pip install test-skill
```
"""
        result = self.validator.validate_skill_structure(content)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_invalid_yaml_frontmatter(self) -> None:
        content = """This is not valid YAML frontmatter
---
name: Test
---
Body content
"""
        result = self.validator.validate_skill_structure(content)
        assert result.is_valid is False
        assert any("Missing or invalid YAML frontmatter" in e for e in result.errors)

    def test_missing_required_fields(self) -> None:
        content = """---
name: "Test Skill"
---
Body content
"""
        result = self.validator.validate_skill_structure(content)
        assert result.is_valid is False
        assert any("Missing required field: description" in e for e in result.errors)
        assert any("Missing required field: category" in e for e in result.errors)

    def test_missing_all_required_fields(self) -> None:
        content = """---
author: "Someone"
---
Body content
"""
        result = self.validator.validate_skill_structure(content)
        assert result.is_valid is False
        assert len(result.errors) >= 3

    def test_name_too_short(self) -> None:
        content = """---
name: "AB"
description: "Test description"
category: "testing"
---
Body content
"""
        result = self.validator.validate_skill_structure(content)
        assert any("Skill name must be at least 3 characters" in e for e in result.errors)

    def test_name_too_long(self) -> None:
        content = f"""---
name: "{'X' * 101}"
description: "Test description"
category: "testing"
---
Body content
"""
        result = self.validator.validate_skill_structure(content)
        assert any("Skill name must be at most 100 characters" in e for e in result.errors)

    def test_name_invalid_characters(self) -> None:
        content = """---
name: "Test@Skill!"
description: "Test description"
category: "testing"
---
Body content
"""
        result = self.validator.validate_skill_structure(content)
        assert any("Skill name contains invalid characters" in e for e in result.errors)

    def test_frontmatter_not_a_dict(self) -> None:
        content = """---
- item1
- item2
---
Body content
"""
        result = self.validator.validate_skill_structure(content)
        assert result.is_valid is False
        assert any("YAML frontmatter must be a dictionary" in e for e in result.errors)

    def test_unclosed_yaml_frontmatter(self) -> None:
        content = """---
name: "Test Skill"
description: "Test"
category: "testing"

Body content without closing
"""
        result = self.validator.validate_skill_structure(content)
        assert result.is_valid is False
        assert any("Missing or invalid YAML frontmatter" in e for e in result.errors)

    def test_valid_version_format(self) -> None:
        assert self.validator.validate_version_format("1.0.0") is True
        assert self.validator.validate_version_format("0.1.0") is True
        assert self.validator.validate_version_format("10.20.30") is True
        assert self.validator.validate_version_format("1.0.0-alpha") is True
        assert self.validator.validate_version_format("1.0.0-alpha.1") is True
        assert self.validator.validate_version_format("1.0.0+build") is True
        assert self.validator.validate_version_format("1.0.0-alpha+build") is True

    def test_invalid_version_format(self) -> None:
        assert self.validator.validate_version_format("1.0") is False
        assert self.validator.validate_version_format("v1.0.0") is False
        assert self.validator.validate_version_format("1.0.0.0") is False
        assert self.validator.validate_version_format("latest") is False
        assert self.validator.validate_version_format("") is False

    def test_version_format_validation_in_structure(self) -> None:
        content = """---
name: "Test Skill"
description: "A test skill"
category: "testing"
version: "invalid-version"
---
Body content
"""
        result = self.validator.validate_skill_structure(content)
        assert any("Invalid version format" in e for e in result.errors)

    def test_tags_not_a_list(self) -> None:
        content = """---
name: "Test Skill"
description: "A test skill"
category: "testing"
tags: "python"
---
Body content
"""
        result = self.validator.validate_skill_structure(content)
        assert any("Tags must be a list" in e for e in result.errors)

    def test_too_many_tags_warning(self) -> None:
        tags = [f"tag{i}" for i in range(25)]
        content = f"""---
name: "Test Skill"
description: "A test skill"
category: "testing"
tags: {tags}
---
Body content
"""
        result = self.validator.validate_skill_structure(content)
        assert any("Too many tags" in w for w in result.warnings)

    def test_unknown_category_warning(self) -> None:
        content = """---
name: "Test Skill"
description: "A test skill"
category: "unknown_category"
---
Body content
"""
        result = self.validator.validate_skill_structure(content)
        assert any("not in the standard list" in w for w in result.warnings)

    def test_valid_category_no_warning(self) -> None:
        content = """---
name: "Test Skill"
description: "A test skill"
category: "code_generation"
---
Body content
"""
        result = self.validator.validate_skill_structure(content)
        assert not any("not in the standard list" in w for w in result.warnings)

    def test_no_content_frontmatter(self) -> None:
        result = self.validator.validate_skill_structure("")
        assert result.is_valid is False
        assert any("Missing or invalid YAML frontmatter" in e for e in result.errors)


class TestDependencyValidation:

    def setup_method(self) -> None:
        self.validator = SkillValidator()

    def test_circular_dependency_detection_direct(self) -> None:
        deps = ["skill-b"]
        existing = {"skill-b": {"dependencies": ["skill-a"]}}

        result = self.validator.validate_dependencies("skill-a", deps, existing)
        assert result.is_valid is False
        assert any("Circular dependency detected" in e for e in result.errors)

    def test_circular_dependency_detection_indirect(self) -> None:
        deps = ["skill-b"]
        existing = {
            "skill-b": {"dependencies": ["skill-c"]},
            "skill-c": {"dependencies": ["skill-a"]},
        }

        result = self.validator.validate_dependencies("skill-a", deps, existing)
        assert result.is_valid is False
        assert any("Circular dependency detected" in e for e in result.errors)

    def test_circular_dependency_self(self) -> None:
        deps = ["skill-a"]
        existing = {}

        result = self.validator.validate_dependencies("skill-a", deps, existing)
        assert result.is_valid is False
        assert any("Skill cannot depend on itself" in e for e in result.errors)

    def test_no_dependency_cycle(self) -> None:
        deps = ["skill-b", "skill-c"]
        existing = {
            "skill-b": {"dependencies": []},
            "skill-c": {"dependencies": []},
        }

        result = self.validator.validate_dependencies("skill-a", deps, existing)
        assert result.is_valid is True

    def test_dependency_not_found_warning(self) -> None:
        deps = ["nonexistent-skill"]
        existing = {}

        result = self.validator.validate_dependencies("skill-a", deps, existing)
        assert any("Dependency not found" in w for w in result.warnings)

    def test_empty_dependencies(self) -> None:
        result = self.validator.validate_dependencies("skill-a", [], {})
        assert result.is_valid is True


class TestQualityScoring:

    def setup_method(self) -> None:
        self.validator = SkillValidator()

    def test_perfect_quality_score(self) -> None:
        skill = {
            "name": "Test Skill",
            "description": "A very comprehensive and detailed description that is well over 100 characters long to get the full description length bonus points",
            "tags": ["python", "testing", "code-generation"],
            "version": "1.0.0",
            "author": "Test Author",
            "license": "MIT",
            "content": """## Usage

This skill is used for testing.

## Examples

```python
print("hello")
```

## Installation

```bash
pip install test
```
""",
        }
        result = self.validator.validate_skill_quality(skill)
        assert result.quality_score > 60
        assert result.is_valid is True

    def test_low_quality_score(self) -> None:
        skill = {
            "name": "Test",
            "description": "",
            "tags": [],
            "content": "short",
        }
        result = self.validator.validate_skill_quality(skill)
        assert result.quality_score < 60
        assert len(result.suggestions) > 0

    def test_quality_score_below_threshold(self) -> None:
        skill = {
            "name": "T",
            "description": "",
            "tags": [],
            "content": "",
        }
        result = self.validator.validate_skill_quality(skill)
        assert result.quality_score < 30
        assert result.is_valid is False
        assert any("Quality score too low" in e for e in result.errors)

    def test_quality_scoring_has_examples(self) -> None:
        skill = {
            "name": "Test",
            "description": "Description",
            "tags": ["python"],
            "version": "1.0.0",
            "author": "Author",
            "license": "MIT",
            "content": """## Examples

```python
print("example")
```
""",
        }
        result = self.validator.validate_skill_quality(skill)
        assert result.quality_score > 0

    def test_quality_scoring_has_usage_instructions(self) -> None:
        skill = {
            "name": "Test",
            "description": "Description",
            "tags": ["python"],
            "version": "1.0.0",
            "author": "Author",
            "license": "MIT",
            "content": """## Usage

Follow these steps to use this skill.
""",
        }
        result = self.validator.validate_skill_quality(skill)
        assert result.quality_score > 0


class TestSkillCompleteness:

    def setup_method(self) -> None:
        self.validator = SkillValidator()

    def test_complete_skill(self) -> None:
        skill = {
            "name": "Complete Skill",
            "description": "A complete skill",
            "category": "testing",
            "version": "1.0.0",
            "author": "Author",
            "tags": ["python", "testing"],
            "license": "MIT",
            "content": "This is a comprehensive skill content that is definitely more than fifty characters long",
        }
        result = self.validator.validate_skill_completeness(skill)
        assert result.is_valid is True

    def test_incomplete_skill_missing_required(self) -> None:
        skill = {
            "name": "Incomplete",
            "content": "short",
        }
        result = self.validator.validate_skill_completeness(skill)
        assert result.is_valid is False
        assert any("Missing required field" in e for e in result.errors)

    def test_skill_content_too_short(self) -> None:
        skill = {
            "name": "Short",
            "description": "A short skill",
            "category": "testing",
            "content": "too short",
        }
        result = self.validator.validate_skill_completeness(skill)
        assert result.is_valid is False
        assert any("Skill content is too short" in e for e in result.errors)

    def test_missing_recommended_fields_warning(self) -> None:
        skill = {
            "name": "Basic Skill",
            "description": "A basic skill",
            "category": "testing",
            "content": "This is a sufficiently long content that meets the minimum requirement of fifty characters",
        }
        result = self.validator.validate_skill_completeness(skill)
        assert result.is_valid is True
        assert len(result.warnings) > 0

    def test_no_tags_warning(self) -> None:
        skill = {
            "name": "No Tags",
            "description": "A skill without tags",
            "category": "testing",
            "version": "1.0.0",
            "author": "Author",
            "license": "MIT",
            "tags": [],
            "content": "Content that is long enough to pass the minimum length check for validation",
        }
        result = self.validator.validate_skill_completeness(skill)
        assert any("No tags provided" in w for w in result.warnings)

    def test_few_tags_suggestion(self) -> None:
        skill = {
            "name": "Single Tag",
            "description": "A skill with one tag",
            "category": "testing",
            "version": "1.0.0",
            "author": "Author",
            "license": "MIT",
            "tags": ["python"],
            "content": "Content that is long enough to pass the minimum length check for validation",
        }
        result = self.validator.validate_skill_completeness(skill)
        assert any("Add more tags" in s for s in result.suggestions)


class TestLintSkillMarkdown:

    def setup_method(self) -> None:
        self.validator = SkillValidator()

    def test_unclosed_fenced_code_block(self) -> None:
        content = """Here is some code:

```python
print("hello")
This is not closed.
"""
        result = self.validator.lint_skill_markdown(content)
        assert result.has_errors is True
        assert any("Unclosed fenced code block" in i["message"] for i in result.issues)

    def test_clean_markdown(self) -> None:
        content = """# Title

This is a paragraph.

```python
print("hello")
```

## Section

More text here.
"""
        result = self.validator.lint_skill_markdown(content)
        has_errors_only = any(i["severity"] == "error" for i in result.issues)
        assert not has_errors_only

    def test_bare_url_detection(self) -> None:
        content = """Check out https://example.com for more info."""
        result = self.validator.lint_skill_markdown(content)
        assert any("Bare URL" in i["message"] for i in result.issues)

    def test_long_heading_warning(self) -> None:
        long_heading = "# " + "A" * 81
        content = long_heading + "\n\nBody text."
        result = self.validator.lint_skill_markdown(content)
        assert any("Heading is too long" in i["message"] for i in result.issues)

    def test_multiple_blank_lines(self) -> None:
        content = """Line 1


Line 2"""
        result = self.validator.lint_skill_markdown(content)
        assert any("Multiple consecutive blank lines" in i["message"] for i in result.issues)

    def test_trailing_whitespace(self) -> None:
        content = "Line with trailing spaces   \nAnother line"
        result = self.validator.lint_skill_markdown(content)
        assert any("Trailing whitespace" in i["message"] for i in result.issues)