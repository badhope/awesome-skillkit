from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    suggestions: List[str] = field(default_factory=list)


@dataclass
class LintResult:
    has_errors: bool
    issues: List[Dict[str, Any]] = field(default_factory=list)


class SkillValidator:

    REQUIRED_FIELDS = ["name", "description", "category"]
    RECOMMENDED_FIELDS = ["version", "author", "tags", "license"]
    VALID_CATEGORIES = {
        "code_generation",
        "debugging",
        "refactoring",
        "testing",
        "documentation",
        "data_analysis",
        "devops",
        "security",
        "communication",
        "workflow",
        "research",
        "teaching",
        "translation",
        "design",
        "other",
    }

    QUALITY_WEIGHTS = {
        "has_description": 15,
        "description_length": 10,
        "has_tags": 10,
        "has_version": 5,
        "has_author": 5,
        "has_examples": 15,
        "has_usage_instructions": 15,
        "has_license": 5,
        "markdown_quality": 10,
        "frontmatter_valid": 10,
    }

    def validate_skill_structure(self, content: str) -> ValidationResult:
        result = ValidationResult(is_valid=True)

        frontmatter, body, parse_error = self.parse_with_frontmatter(content)

        if parse_error == "missing":
            result.is_valid = False
            result.errors.append("Missing or invalid YAML frontmatter")
            return result
        if parse_error == "not_dict":
            result.is_valid = False
            result.errors.append("YAML frontmatter must be a dictionary")
            return result
        if frontmatter is None:
            result.is_valid = False
            result.errors.append("Missing or invalid YAML frontmatter")
            return result

        for key in self.REQUIRED_FIELDS:
            if key not in frontmatter or not frontmatter[key]:
                result.is_valid = False
                result.errors.append(f"Missing required field: {key}")

        if "name" in frontmatter:
            name = str(frontmatter["name"])
            if len(name) < 3:
                result.errors.append("Skill name must be at least 3 characters")
            if len(name) > 100:
                result.errors.append("Skill name must be at most 100 characters")
            if not re.match(r"^[a-zA-Z0-9_\- ]+$", name):
                result.errors.append("Skill name contains invalid characters")

        if "category" in frontmatter:
            category = str(frontmatter["category"]).lower()
            if category not in self.VALID_CATEGORIES:
                result.warnings.append(
                    f"Category '{category}' is not in the standard list"
                )

        if "version" in frontmatter:
            version = str(frontmatter["version"])
            if not self.validate_version_format(version):
                result.errors.append(f"Invalid version format: {version}")

        if "tags" in frontmatter:
            tags = frontmatter["tags"]
            if not isinstance(tags, list):
                result.errors.append("Tags must be a list")
            elif len(tags) > 20:
                result.warnings.append("Too many tags (max 20 recommended)")

        markdown_issues = self.lint_skill_markdown(body)
        if markdown_issues.has_errors:
            for issue in markdown_issues.issues:
                if issue.get("severity") == "error":
                    result.warnings.append(f"Markdown issue: {issue.get('message')}")

        result.is_valid = len(result.errors) == 0
        return result

    def validate_dependencies(
        self,
        skill_id: str,
        deps: List[str],
        existing_skills: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        existing_skills = existing_skills or {}

        cycle = self._detect_dependency_cycle(skill_id, deps, existing_skills)
        if cycle:
            result.is_valid = False
            result.errors.append(f"Circular dependency detected: {' -> '.join(cycle)}")

        for dep_id in deps:
            if dep_id == skill_id:
                result.is_valid = False
                result.errors.append(f"Skill cannot depend on itself: {dep_id}")
            if dep_id not in existing_skills:
                result.warnings.append(f"Dependency not found: {dep_id}")

        return result

    def _detect_dependency_cycle(
        self,
        skill_id: str,
        deps: List[str],
        existing_skills: Dict[str, Any],
    ) -> Optional[List[str]]:
        def dfs(current: str, visited: Set[str], path: List[str]) -> Optional[List[str]]:
            if current in visited:
                if current in path:
                    cycle_start = path.index(current)
                    return path[cycle_start:] + [current]
                return None

            visited.add(current)
            path.append(current)

            child_deps = []
            if current in existing_skills:
                child_deps = existing_skills[current].get("dependencies", [])
            elif current == skill_id:
                child_deps = deps

            for dep in child_deps:
                result = dfs(dep, visited, list(path))
                if result:
                    return result

            return None

        return dfs(skill_id, set(), [])

    def validate_version_format(self, version: str) -> bool:
        semver_pattern = re.compile(
            r"^"
            r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
            r"(-[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?"
            r"(\+[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?"
            r"$"
        )
        return bool(semver_pattern.match(version))

    def validate_skill_completeness(self, skill: Dict[str, Any]) -> ValidationResult:
        result = ValidationResult(is_valid=True)

        for key in self.REQUIRED_FIELDS:
            if key not in skill or not skill[key]:
                result.is_valid = False
                result.errors.append(f"Missing required field: {key}")

        for key in self.RECOMMENDED_FIELDS:
            if key not in skill or not skill[key]:
                result.warnings.append(f"Missing recommended field: {key}")

        if "tags" in skill and isinstance(skill["tags"], list):
            if len(skill["tags"]) == 0:
                result.warnings.append("No tags provided")
            if len(skill["tags"]) < 2:
                result.suggestions.append("Add more tags for better discoverability")

        content = skill.get("content", "")
        if not content or len(content.strip()) < 50:
            result.is_valid = False
            result.errors.append("Skill content is too short (minimum 50 characters)")

        return result

    def validate_skill_quality(self, skill: Dict[str, Any]) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        total_score = 0.0
        max_score = sum(self.QUALITY_WEIGHTS.values())

        description = skill.get("description", "")
        if description and len(description) > 0:
            total_score += self.QUALITY_WEIGHTS["has_description"]
        if description and len(description) >= 100:
            total_score += self.QUALITY_WEIGHTS["description_length"]
        else:
            result.suggestions.append("Add a more detailed description (100+ chars)")

        tags = skill.get("tags", [])
        if tags and len(tags) > 0:
            total_score += self.QUALITY_WEIGHTS["has_tags"]
        else:
            result.suggestions.append("Add tags for better discoverability")

        if skill.get("version"):
            total_score += self.QUALITY_WEIGHTS["has_version"]

        if skill.get("author"):
            total_score += self.QUALITY_WEIGHTS["has_author"]

        content = skill.get("content", "")
        if self._has_examples(content):
            total_score += self.QUALITY_WEIGHTS["has_examples"]
        else:
            result.suggestions.append("Include code examples in the skill content")

        if self._has_usage_instructions(content):
            total_score += self.QUALITY_WEIGHTS["has_usage_instructions"]
        else:
            result.suggestions.append("Add usage instructions")

        if skill.get("license"):
            total_score += self.QUALITY_WEIGHTS["has_license"]
        else:
            result.suggestions.append("Specify a license")

        markdown_issues = self.lint_skill_markdown(content)
        markdown_penalty = len(markdown_issues.issues) * 2
        markdown_score = max(0, self.QUALITY_WEIGHTS["markdown_quality"] - markdown_penalty)
        total_score += markdown_score

        # Frontmatter validity: parse the content's YAML once and reuse the
        # result. The previous implementation called `validate_skill_structure`
        # which re-parsed the same content, doubling the work and giving
        # callers two different ValidationResult objects to reconcile.
        frontmatter, _body, fm_error = self.parse_with_frontmatter(content)
        if not fm_error and frontmatter is not None:
            total_score += self.QUALITY_WEIGHTS["frontmatter_valid"]

        normalized_score = round((total_score / max_score) * 100, 1)
        result.quality_score = min(normalized_score, 100.0)

        if result.quality_score < 30:
            result.is_valid = False
            result.errors.append(f"Quality score too low: {result.quality_score}")
        elif result.quality_score < 60:
            result.warnings.append(f"Quality score could be improved: {result.quality_score}")

        return result

    def _has_examples(self, content: str) -> bool:
        example_patterns = [
            r"```\w*\s*\n[\s\S]*?```",
            r"##\s*Example",
            r"##\s*Examples",
            r"###\s*Example",
            r"###\s*Examples",
        ]
        for pattern in example_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def _has_usage_instructions(self, content: str) -> bool:
        usage_patterns = [
            r"##\s*Usage",
            r"##\s*How to use",
            r"##\s*Getting Started",
            r"##\s*Installation",
            r"##\s*Quickstart",
        ]
        for pattern in usage_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def lint_skill_markdown(self, content: str) -> LintResult:
        # Hand-rolled subset of commonmark rules. Not trying to be a real
        # markdownlint — we only flag the things that actually trip us up
        # during skill review. Add rules sparingly; every false positive
        # here is a PR we don't want to take.
        issues: List[Dict[str, Any]] = []

        fenced_blocks = re.findall(r"```", content)
        if len(fenced_blocks) % 2 != 0:
            issues.append({
                "line": self._estimate_line(content, content.rfind("```")),
                "severity": "error",
                "message": "Unclosed fenced code block",
                "rule": "MD040",
            })

        raw_html = re.findall(r"<(div|span|table|script|style)", content)
        for tag in raw_html:
            issues.append({
                "line": self._estimate_line(content, content.index(f"<{tag}")),
                "severity": "warning",
                "message": f"Raw HTML tag <{tag}> found",
                "rule": "MD033",
            })

        bare_urls = re.findall(r"(?<!<)https?://\S+", content)
        for url in bare_urls:
            pos = content.index(url)
            if pos > 0 and content[pos - 1] != "(":
                issues.append({
                    "line": self._estimate_line(content, pos),
                    "severity": "warning",
                    "message": f"Bare URL found: {url[:50]}...",
                    "rule": "MD034",
                })

        heading_lines = re.findall(r"^#+\s+.*$", content, re.MULTILINE)
        for match in heading_lines:
            heading_text = match.lstrip("#").strip()
            if len(heading_text) > 80:
                pos = content.index(match)
                issues.append({
                    "line": self._estimate_line(content, pos),
                    "severity": "warning",
                    "message": "Heading is too long (max 80 chars)",
                    "rule": "MD003-style",
                })

        blank_lines_pattern = re.compile(r"\n{3,}")
        for match in blank_lines_pattern.finditer(content):
            issues.append({
                "line": self._estimate_line(content, match.start()),
                "severity": "warning",
                "message": "Multiple consecutive blank lines",
                "rule": "MD012",
            })

        trailing_spaces = re.findall(r"[ \t]+$", content, re.MULTILINE)
        if trailing_spaces:
            issues.append({
                "line": self._estimate_line(content, content.rfind(trailing_spaces[0])),
                "severity": "warning",
                "message": "Trailing whitespace found",
                "rule": "MD009",
            })

        list_items = re.findall(r"^(\s*)[*+-]\s+", content, re.MULTILINE)
        if list_items:
            indent_levels = [len(indent) for indent in list_items]
            if len(set(indent_levels)) > 5:
                issues.append({
                    "line": len(content.split("\n")),
                    "severity": "warning",
                    "message": "Too many list indent levels",
                })

        return LintResult(
            has_errors=bool(issues),
            issues=issues,
        )

    def _estimate_line(self, content: str, pos: int) -> int:
        return content[:pos].count("\n") + 1

    def parse_with_frontmatter(
        self, content: str
    ) -> Tuple[Optional[Any], str, str]:
        """Single source of truth for frontmatter parsing.

        Returns (frontmatter, body, parse_error) where parse_error is one
        of:
          - "" on success (frontmatter is a dict, body is the markdown)
          - "missing" if the `---` fence is absent or unterminated
          - "not_dict" if the YAML is valid but not a mapping
        """
        content = content.strip()

        if not content.startswith("---"):
            return None, content, "missing"

        rest = content[3:]
        end_idx = rest.find("---")
        if end_idx == -1:
            return None, content, "missing"

        frontmatter_str = rest[:end_idx].strip()
        body = rest[end_idx + 3:].strip()

        try:
            frontmatter = yaml.safe_load(frontmatter_str)
        except yaml.YAMLError:
            return None, content, "missing"

        if not isinstance(frontmatter, dict):
            return frontmatter, body, "not_dict"

        return frontmatter, body, ""
