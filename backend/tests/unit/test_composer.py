import pytest

from app.services.skill_composer import (
    CompositionResult,
    DependencyTree,
    SkillComposer,
    WorkflowNode,
    WorkflowNodeType,
)


class TestSkillComposer:

    def setup_method(self) -> None:
        self.registry = {
            "skill-a": {
                "id": "skill-a",
                "name": "Skill A",
                "description": "First skill",
                "category": "code_generation",
                "tags": ["python", "testing"],
                "dependencies": [],
                "resources": ["cpu"],
            },
            "skill-b": {
                "id": "skill-b",
                "name": "Skill B",
                "description": "Second skill",
                "category": "debugging",
                "tags": ["python", "debug"],
                "dependencies": ["skill-a"],
                "resources": ["memory"],
            },
            "skill-c": {
                "id": "skill-c",
                "name": "Skill C",
                "description": "Third skill",
                "category": "testing",
                "tags": ["python", "test"],
                "dependencies": [],
                "resources": ["cpu"],
            },
            "skill-d": {
                "id": "skill-d",
                "name": "Skill D",
                "description": "Fourth skill",
                "category": "refactoring",
                "tags": ["python", "refactor"],
                "dependencies": ["skill-b", "skill-c"],
                "resources": ["disk"],
            },
        }
        self.composer = SkillComposer(skill_registry=self.registry)

    def test_sequential_composition(self) -> None:
        skill_ids = ["skill-a", "skill-b", "skill-c"]
        result = self.composer.compose_skills(
            skill_ids, config={"mode": "sequential"}
        )

        assert result.is_valid is True
        assert len(result.workflow_nodes) > 3
        assert len(result.workflow_edges) > 0

        start_node = next((n for n in result.workflow_nodes if n.type == WorkflowNodeType.START), None)
        end_node = next((n for n in result.workflow_nodes if n.type == WorkflowNodeType.END), None)
        assert start_node is not None
        assert end_node is not None

        skill_nodes = [n for n in result.workflow_nodes if n.type == WorkflowNodeType.SKILL]
        assert len(skill_nodes) == 3

    def test_parallel_composition(self) -> None:
        skill_ids = ["skill-a", "skill-b", "skill-c"]
        result = self.composer.compose_skills(
            skill_ids, config={"mode": "parallel"}
        )

        assert result.is_valid is True

        fork_node = next((n for n in result.workflow_nodes if n.type == WorkflowNodeType.PARALLEL), None)
        join_node = next((n for n in result.workflow_nodes if n.type == WorkflowNodeType.MERGE), None)
        assert fork_node is not None
        assert join_node is not None

        skill_nodes = [n for n in result.workflow_nodes if n.type == WorkflowNodeType.SKILL]
        assert len(skill_nodes) == 3

    def test_dag_workflow(self) -> None:
        skill_ids = ["skill-a", "skill-b", "skill-c", "skill-d"]
        result = self.composer.compose_skills(
            skill_ids, config={"mode": "dag"}
        )

        assert result.is_valid is True

        skill_nodes = [n for n in result.workflow_nodes if n.type == WorkflowNodeType.SKILL]
        assert len(skill_nodes) == 4

    def test_conditional_workflow(self) -> None:
        skill_ids = ["skill-a", "skill-b", "skill-c"]
        result = self.composer.compose_skills(
            skill_ids, config={"mode": "conditional"}
        )

        assert result.is_valid is True

        condition_nodes = [n for n in result.workflow_nodes if n.type == WorkflowNodeType.CONDITION]
        assert len(condition_nodes) >= 2

    def test_dependency_resolution(self) -> None:
        trees = self.composer.resolve_dependencies(["skill-d"])

        assert len(trees) == 1
        tree = trees[0]
        assert tree.skill_id == "skill-d"
        assert tree.name == "Skill D"
        assert len(tree.dependencies) == 2

        dep_ids = [d.skill_id for d in tree.dependencies]
        assert "skill-b" in dep_ids
        assert "skill-c" in dep_ids

    def test_dependency_tree_depth(self) -> None:
        trees = self.composer.resolve_dependencies(["skill-d"])
        assert len(trees) == 1

        tree = trees[0]
        assert tree.depth == 0
        for child in tree.dependencies:
            assert child.depth == 1
            for grandchild in child.dependencies:
                assert grandchild.depth == 2

    def test_composition_validation_empty_skills(self) -> None:
        result = self.composer.validate_composition([])
        assert result["valid"] is False
        assert any("No skill IDs provided" in e for e in result["errors"])

    def test_composition_validation_too_many_skills(self) -> None:
        skill_ids = [f"skill-{i}" for i in range(25)]
        result = self.composer.validate_composition(skill_ids)
        assert result["valid"] is False
        assert any("Too many skills" in e for e in result["errors"])

    def test_composition_validation_skill_not_found(self) -> None:
        result = self.composer.validate_composition(["nonexistent"])
        assert result["valid"] is False
        assert any("Skill not found" in e for e in result["errors"])

    def test_composition_validation_invalid_mode(self) -> None:
        result = self.composer.validate_composition(
            ["skill-a"], config={"mode": "invalid_mode"}
        )
        assert result["valid"] is False
        assert any("Invalid mode" in e for e in result["errors"])

    def test_composition_validation_valid(self) -> None:
        result = self.composer.validate_composition(
            ["skill-a", "skill-b"], config={"mode": "sequential"}
        )
        assert result["valid"] is True

    def test_composition_too_many_skills_error(self) -> None:
        skill_ids = [f"skill-{i}" for i in range(25)]
        result = self.composer.compose_skills(skill_ids)
        assert result.is_valid is False
        assert any("Too many skills" in e for e in result.errors)

    def test_composition_validation_with_conditions(self) -> None:
        result = self.composer.validate_composition(
            ["skill-a", "skill-b"],
            config={
                "mode": "conditional",
                "conditions": {
                    "skill-b": {"if": "previous_success"},
                },
            },
        )
        assert result["valid"] is True

    def test_composition_validation_missing_condition_warning(self) -> None:
        result = self.composer.validate_composition(
            ["skill-a", "skill-b"],
            config={
                "mode": "conditional",
                "conditions": {
                    "skill-a": {},
                },
            },
        )
        assert result["valid"] is True
        assert any("No condition specified" in w for w in result["warnings"])

    def test_composition_execution_order(self) -> None:
        skill_ids = ["skill-a", "skill-b", "skill-c", "skill-d"]
        result = self.composer.compose_skills(
            skill_ids, config={"mode": "dag"}
        )

        assert result.is_valid is True
        assert len(result.execution_order) > 0

    def test_optimization_single_skill(self) -> None:
        suggestions = self.composer.optimize_composition(["skill-a"])
        assert len(suggestions) > 0
        assert any("Only one skill" in s for s in suggestions)

    def test_optimization_multiple_skills(self) -> None:
        suggestions = self.composer.optimize_composition(
            ["skill-a", "skill-b", "skill-c", "skill-d"]
        )
        assert isinstance(suggestions, list)

    def test_find_parallelizable_skills(self) -> None:
        self.composer.update_registry({
            "skill-x": {
                "id": "skill-x",
                "name": "Skill X",
                "category": "code_generation",
                "tags": ["js"],
                "dependencies": [],
                "resources": [],
            },
            "skill-y": {
                "id": "skill-y",
                "name": "Skill Y",
                "category": "debugging",
                "tags": ["go"],
                "dependencies": [],
                "resources": [],
            },
        })
        suggestions = self.composer.optimize_composition(["skill-x", "skill-y"])
        assert isinstance(suggestions, list)

    def test_redundant_skills_detection(self) -> None:
        self.composer.update_registry({
            "skill-e": {
                "id": "skill-e",
                "name": "Skill E",
                "category": "code_generation",
                "tags": ["python", "code", "generation", "ai"],
                "dependencies": [],
            },
            "skill-f": {
                "id": "skill-f",
                "name": "Skill F",
                "category": "code_generation",
                "tags": ["python", "code", "generation", "ai"],
                "dependencies": [],
            },
        })
        suggestions = self.composer.optimize_composition(["skill-e", "skill-f"])
        assert isinstance(suggestions, list)

    def test_update_registry(self) -> None:
        self.composer.update_registry({
            "new-skill": {
                "id": "new-skill",
                "name": "New Skill",
                "category": "security",
                "tags": [],
                "dependencies": [],
            },
        })
        assert "new-skill" in self.composer.skill_registry
        assert self.composer.skill_registry["new-skill"]["name"] == "New Skill"

    def test_composition_validation_category_conflicts(self) -> None:
        self.composer.update_registry({
            "skill-e": {
                "id": "skill-e",
                "name": "Skill E",
                "category": "category1",
                "tags": [],
                "dependencies": [],
            },
            "skill-f": {
                "id": "skill-f",
                "name": "Skill F",
                "category": "category2",
                "tags": [],
                "dependencies": [],
            },
            "skill-g": {
                "id": "skill-g",
                "name": "Skill G",
                "category": "category3",
                "tags": [],
                "dependencies": [],
            },
            "skill-h": {
                "id": "skill-h",
                "name": "Skill H",
                "category": "category4",
                "tags": [],
                "dependencies": [],
            },
        })
        result = self.composer.validate_composition(["skill-e", "skill-f", "skill-g", "skill-h"])
        assert any("spans" in w for w in result["warnings"])

    def test_dependency_tree_circular_handling(self) -> None:
        self.composer.update_registry({
            "circ-a": {
                "id": "circ-a",
                "name": "Circular A",
                "category": "testing",
                "tags": [],
                "dependencies": ["circ-b"],
            },
            "circ-b": {
                "id": "circ-b",
                "name": "Circular B",
                "category": "testing",
                "tags": [],
                "dependencies": ["circ-a"],
            },
        })
        trees = self.composer.resolve_dependencies(["circ-a"])
        assert len(trees) == 1

    def test_composition_validation_unresolvable_dependencies(self) -> None:
        self.composer.update_registry({
            "skill-z": {
                "id": "skill-z",
                "name": "Skill Z",
                "category": "testing",
                "tags": [],
                "dependencies": ["totally-missing-skill"],
            },
        })
        result = self.composer.validate_composition(["skill-z"])
        assert any("Unresolvable dependencies" in e for e in result["errors"])


class TestWorkflowNode:

    def test_workflow_node_creation(self) -> None:
        node = WorkflowNode(
            id="skill_1",
            type=WorkflowNodeType.SKILL,
            label="My Skill",
            skill_id="skill-a",
            config={"timeout": 30},
            depends_on=["start"],
        )
        assert node.id == "skill_1"
        assert node.type == WorkflowNodeType.SKILL
        assert node.label == "My Skill"
        assert node.skill_id == "skill-a"
        assert node.config == {"timeout": 30}
        assert node.depends_on == ["start"]


class TestDependencyTree:

    def test_dependency_tree_creation(self) -> None:
        child = DependencyTree(
            skill_id="skill-b",
            name="Skill B",
            depth=1,
        )
        tree = DependencyTree(
            skill_id="skill-a",
            name="Skill A",
            dependencies=[child],
            depth=0,
        )
        assert tree.skill_id == "skill-a"
        assert tree.name == "Skill A"
        assert len(tree.dependencies) == 1
        assert tree.dependencies[0].skill_id == "skill-b"
        assert tree.depth == 0
        assert tree.dependencies[0].depth == 1


class TestCompositionResult:

    def test_composition_result_valid(self) -> None:
        result = CompositionResult(
            is_valid=True,
            execution_order=["skill-a", "skill-b", "skill-c"],
        )
        assert result.is_valid is True
        assert result.execution_order == ["skill-a", "skill-b", "skill-c"]
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_composition_result_invalid(self) -> None:
        result = CompositionResult(
            is_valid=False,
            errors=["Error 1", "Error 2"],
            warnings=["Warning 1"],
            suggestions=["Suggestion 1"],
        )
        assert result.is_valid is False
        assert len(result.errors) == 2
        assert len(result.warnings) == 1
        assert len(result.suggestions) == 1