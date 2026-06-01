from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx


class WorkflowNodeType(str, Enum):
    START = "start"
    END = "end"
    SKILL = "skill"
    CONDITION = "condition"
    PARALLEL = "parallel"
    MERGE = "merge"


@dataclass
class WorkflowNode:
    id: str
    type: WorkflowNodeType
    label: str
    skill_id: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)


@dataclass
class WorkflowEdge:
    source: str
    target: str
    label: str = ""
    condition: Optional[str] = None


@dataclass
class CompositionResult:
    is_valid: bool
    workflow_nodes: List[WorkflowNode] = field(default_factory=list)
    workflow_edges: List[WorkflowEdge] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class DependencyTree:
    skill_id: str
    name: str
    dependencies: List[DependencyTree] = field(default_factory=list)
    depth: int = 0


class SkillComposer:

    MAX_COMPOSITION_SIZE = 20
    MAX_DEPTH = 10

    def __init__(self, skill_registry: Optional[Dict[str, Any]] = None):
        self.skill_registry: Dict[str, Any] = skill_registry or {}

    def update_registry(self, skills: Dict[str, Any]) -> None:
        self.skill_registry.update(skills)

    def compose_skills(
        self,
        skill_ids: List[str],
        config: Optional[Dict[str, Any]] = None,
    ) -> CompositionResult:
        config = config or {}

        if len(skill_ids) > self.MAX_COMPOSITION_SIZE:
            return CompositionResult(
                is_valid=False,
                errors=[f"Too many skills (max {self.MAX_COMPOSITION_SIZE})"],
            )

        validation = self.validate_composition(skill_ids, config)
        if not validation["valid"]:
            return CompositionResult(
                is_valid=False,
                errors=validation.get("errors", []),
                warnings=validation.get("warnings", []),
            )

        mode = config.get("mode", "sequential")
        workflow = self.generate_workflow(skill_ids, mode)

        execution_order = self._resolve_execution_order(workflow)
        workflow.execution_order = execution_order

        suggestions = self.optimize_composition(skill_ids)
        workflow.suggestions = suggestions

        return workflow

    def validate_composition(
        self,
        skill_ids: List[str],
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []

        if not skill_ids:
            errors.append("No skill IDs provided")
            return {"valid": False, "errors": errors, "warnings": warnings}

        if len(skill_ids) > self.MAX_COMPOSITION_SIZE:
            errors.append(f"Too many skills: {len(skill_ids)} (max {self.MAX_COMPOSITION_SIZE})")
            return {"valid": False, "errors": errors, "warnings": warnings}

        for skill_id in skill_ids:
            if skill_id not in self.skill_registry:
                errors.append(f"Skill not found: {skill_id}")

        if errors:
            return {"valid": False, "errors": errors, "warnings": warnings}

        dependency_issues = self._check_composition_dependencies(skill_ids)
        errors.extend(dependency_issues["errors"])
        warnings.extend(dependency_issues["warnings"])

        category_conflicts = self._check_category_conflicts(skill_ids)
        warnings.extend(category_conflicts)

        config = config or {}
        mode = config.get("mode", "sequential")
        valid_modes = {"sequential", "parallel", "conditional", "dag"}
        if mode not in valid_modes:
            errors.append(f"Invalid mode: {mode}. Valid modes: {valid_modes}")

        if mode == "conditional":
            conditions = config.get("conditions", {})
            for skill_id in skill_ids:
                if skill_id in conditions:
                    condition = conditions[skill_id]
                    if not isinstance(condition, dict) or "if" not in condition:
                        warnings.append(f"No condition specified for {skill_id}")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _check_composition_dependencies(
        self, skill_ids: List[str]
    ) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []

        all_deps: Set[str] = set()
        for skill_id in skill_ids:
            skill = self.skill_registry.get(skill_id, {})
            deps = skill.get("dependencies", [])
            for dep in deps:
                all_deps.add(dep)

        missing_deps = all_deps - set(skill_ids) - set(self.skill_registry.keys())
        if missing_deps:
            errors.append(f"Unresolvable dependencies: {', '.join(sorted(missing_deps))}")

        for skill_id in skill_ids:
            skill = self.skill_registry.get(skill_id, {})
            deps = set(skill.get("dependencies", []))
            unresolved = deps - set(skill_ids) - set(self.skill_registry.keys())
            if unresolved:
                warnings.append(f"Skill {skill_id} has unresolved deps: {', '.join(sorted(unresolved))}")

        return {"errors": errors, "warnings": warnings}

    def _check_category_conflicts(self, skill_ids: List[str]) -> List[str]:
        warnings: List[str] = []
        categories: Dict[str, List[str]] = {}

        for skill_id in skill_ids:
            skill = self.skill_registry.get(skill_id, {})
            category = skill.get("category", "other")
            if category not in categories:
                categories[category] = []
            categories[category].append(skill_id)

        if len(categories) > 3:
            warnings.append(
                f"Composition spans {len(categories)} categories, "
                "consider grouping related skills"
            )

        return warnings

    def resolve_dependencies(self, skill_ids: List[str]) -> List[DependencyTree]:
        trees: List[DependencyTree] = []

        for skill_id in skill_ids:
            tree = self._build_dependency_tree(skill_id, visited=set(), depth=0)
            if tree:
                trees.append(tree)

        return trees

    def _build_dependency_tree(
        self,
        skill_id: str,
        visited: Set[str],
        depth: int,
    ) -> Optional[DependencyTree]:
        if depth > self.MAX_DEPTH:
            return None

        if skill_id in visited:
            return DependencyTree(
                skill_id=skill_id,
                name=f"{skill_id} (circular)",
                depth=depth,
            )

        skill = self.skill_registry.get(skill_id, {})
        if not skill:
            return None

        visited.add(skill_id)
        name = skill.get("name", skill_id)
        dependencies = skill.get("dependencies", [])

        children: List[DependencyTree] = []
        for dep_id in dependencies:
            child = self._build_dependency_tree(dep_id, visited.copy(), depth + 1)
            if child:
                children.append(child)

        return DependencyTree(
            skill_id=skill_id,
            name=name,
            dependencies=children,
            depth=depth,
        )

    def generate_workflow(
        self,
        skill_ids: List[str],
        mode: str = "sequential",
    ) -> CompositionResult:
        nodes: List[WorkflowNode] = []
        edges: List[WorkflowEdge] = []

        start_node = WorkflowNode(
            id="start",
            type=WorkflowNodeType.START,
            label="Start",
        )
        nodes.append(start_node)

        end_node = WorkflowNode(
            id="end",
            type=WorkflowNodeType.END,
            label="End",
        )
        nodes.append(end_node)

        if mode == "sequential":
            self._build_sequential_workflow(skill_ids, nodes, edges, start_node, end_node)
        elif mode == "parallel":
            self._build_parallel_workflow(skill_ids, nodes, edges, start_node, end_node)
        elif mode == "conditional":
            self._build_conditional_workflow(skill_ids, nodes, edges, start_node, end_node)
        elif mode == "dag":
            self._build_dag_workflow(skill_ids, nodes, edges, start_node, end_node)

        return CompositionResult(
            is_valid=True,
            workflow_nodes=nodes,
            workflow_edges=edges,
        )

    def _build_sequential_workflow(
        self,
        skill_ids: List[str],
        nodes: List[WorkflowNode],
        edges: List[WorkflowEdge],
        start_node: WorkflowNode,
        end_node: WorkflowNode,
    ) -> None:
        prev_id = start_node.id

        for i, skill_id in enumerate(skill_ids):
            skill = self.skill_registry.get(skill_id, {})
            node = WorkflowNode(
                id=f"skill_{i}",
                type=WorkflowNodeType.SKILL,
                label=skill.get("name", skill_id),
                skill_id=skill_id,
                depends_on=[prev_id] if i > 0 else [],
            )
            nodes.append(node)
            edges.append(WorkflowEdge(source=prev_id, target=node.id))
            prev_id = node.id

        edges.append(WorkflowEdge(source=prev_id, target=end_node.id))

    def _build_parallel_workflow(
        self,
        skill_ids: List[str],
        nodes: List[WorkflowNode],
        edges: List[WorkflowEdge],
        start_node: WorkflowNode,
        end_node: WorkflowNode,
    ) -> None:
        fork_node = WorkflowNode(
            id="fork",
            type=WorkflowNodeType.PARALLEL,
            label="Parallel Start",
        )
        join_node = WorkflowNode(
            id="join",
            type=WorkflowNodeType.MERGE,
            label="Parallel End",
        )
        nodes.extend([fork_node, join_node])

        edges.append(WorkflowEdge(source=start_node.id, target=fork_node.id))

        for i, skill_id in enumerate(skill_ids):
            skill = self.skill_registry.get(skill_id, {})
            node = WorkflowNode(
                id=f"skill_{i}",
                type=WorkflowNodeType.SKILL,
                label=skill.get("name", skill_id),
                skill_id=skill_id,
            )
            nodes.append(node)
            edges.append(WorkflowEdge(source=fork_node.id, target=node.id))
            edges.append(WorkflowEdge(source=node.id, target=join_node.id))

        edges.append(WorkflowEdge(source=join_node.id, target=end_node.id))

    def _build_conditional_workflow(
        self,
        skill_ids: List[str],
        nodes: List[WorkflowNode],
        edges: List[WorkflowEdge],
        start_node: WorkflowNode,
        end_node: WorkflowNode,
    ) -> None:
        prev_id = start_node.id

        for i, skill_id in enumerate(skill_ids):
            skill = self.skill_registry.get(skill_id, {})
            node = WorkflowNode(
                id=f"skill_{i}",
                type=WorkflowNodeType.SKILL,
                label=skill.get("name", skill_id),
                skill_id=skill_id,
            )

            if i > 0:
                cond_node = WorkflowNode(
                    id=f"condition_{i}",
                    type=WorkflowNodeType.CONDITION,
                    label=f"Condition for {skill.get('name', skill_id)}",
                )
                nodes.append(cond_node)
                edges.append(WorkflowEdge(source=prev_id, target=cond_node.id))
                edges.append(WorkflowEdge(
                    source=cond_node.id,
                    target=node.id,
                    label="true",
                    condition="previous_success",
                ))
                edges.append(WorkflowEdge(
                    source=cond_node.id,
                    target=end_node.id,
                    label="false",
                    condition="previous_failure",
                ))
            else:
                edges.append(WorkflowEdge(source=prev_id, target=node.id))

            nodes.append(node)
            prev_id = node.id

        edges.append(WorkflowEdge(source=prev_id, target=end_node.id))

    def _build_dag_workflow(
        self,
        skill_ids: List[str],
        nodes: List[WorkflowNode],
        edges: List[WorkflowEdge],
        start_node: WorkflowNode,
        end_node: WorkflowNode,
    ) -> None:
        graph = nx.DiGraph()

        for skill_id in skill_ids:
            skill = self.skill_registry.get(skill_id, {})
            graph.add_node(skill_id, name=skill.get("name", skill_id))

        for skill_id in skill_ids:
            skill = self.skill_registry.get(skill_id, {})
            for dep_id in skill.get("dependencies", []):
                if dep_id in skill_ids:
                    graph.add_edge(dep_id, skill_id)

        skill_nodes: Dict[str, WorkflowNode] = {}
        for skill_id in skill_ids:
            skill = self.skill_registry.get(skill_id, {})
            node = WorkflowNode(
                id=f"skill_{skill_ids.index(skill_id)}",
                type=WorkflowNodeType.SKILL,
                label=skill.get("name", skill_id),
                skill_id=skill_id,
            )
            skill_nodes[skill_id] = node
            nodes.append(node)

        try:
            topological_order = list(nx.topological_sort(graph))
        except nx.NetworkXUnfeasible:
            topological_order = skill_ids

        roots = [n for n in topological_order if graph.in_degree(n) == 0]
        for root in roots:
            edges.append(WorkflowEdge(
                source=start_node.id,
                target=skill_nodes[root].id,
            ))

        for skill_id in topological_order:
            successors = list(graph.successors(skill_id))
            for successor in successors:
                edges.append(WorkflowEdge(
                    source=skill_nodes[skill_id].id,
                    target=skill_nodes[successor].id,
                ))

        leaves = [n for n in topological_order if graph.out_degree(n) == 0]
        for leaf in leaves:
            edges.append(WorkflowEdge(
                source=skill_nodes[leaf].id,
                target=end_node.id,
            ))

    def _resolve_execution_order(self, composition: CompositionResult) -> List[str]:
        node_ids: List[str] = []

        for node in composition.workflow_nodes:
            if node.type == WorkflowNodeType.SKILL and node.skill_id:
                node_ids.append(node.skill_id)

        if not node_ids:
            return node_ids

        graph = nx.DiGraph()
        for node_id in node_ids:
            graph.add_node(node_id)

        for edge in composition.workflow_edges:
            source_node = self._find_node_by_id(composition.workflow_nodes, edge.source)
            target_node = self._find_node_by_id(composition.workflow_nodes, edge.target)
            if source_node and target_node:
                if source_node.skill_id and target_node.skill_id:
                    graph.add_edge(source_node.skill_id, target_node.skill_id)

        try:
            return list(nx.topological_sort(graph))
        except nx.NetworkXUnfeasible:
            return node_ids

    def _find_node_by_id(
        self,
        nodes: List[WorkflowNode],
        node_id: str,
    ) -> Optional[WorkflowNode]:
        for node in nodes:
            if node.id == node_id:
                return node
        return None

    def optimize_composition(self, skill_ids: List[str]) -> List[str]:
        suggestions: List[str] = []

        if len(skill_ids) == 1:
            suggestions.append(
                "Only one skill in composition; consider using it directly"
            )
            return suggestions

        parallel_candidates = self._find_parallelizable_skills(skill_ids)
        if parallel_candidates:
            groups = ", ".join(
                " + ".join(group) for group in parallel_candidates
            )
            suggestions.append(
                f"Skills that can run in parallel: {groups}"
            )

        redundant = self._find_redundant_skills(skill_ids)
        if redundant:
            suggestions.append(
                f"Potentially redundant skills: {', '.join(redundant)}"
            )

        missing_links = self._suggest_missing_links(skill_ids)
        if missing_links:
            suggestions.append(
                f"Consider adding these connections: {', '.join(missing_links)}"
            )

        return suggestions

    def _find_parallelizable_skills(self, skill_ids: List[str]) -> List[Tuple[str, ...]]:
        graph = nx.DiGraph()
        for skill_id in skill_ids:
            skill = self.skill_registry.get(skill_id, {})
            graph.add_node(skill_id)
            for dep in skill.get("dependencies", []):
                if dep in skill_ids:
                    graph.add_edge(dep, skill_id)

        candidates: List[Tuple[str, ...]] = []
        skill_list = list(skill_ids)

        for i in range(len(skill_list)):
            for j in range(i + 1, len(skill_list)):
                a, b = skill_list[i], skill_list[j]
                if not nx.has_path(graph, a, b) and not nx.has_path(graph, b, a):
                    if not self._has_conflict(a, b):
                        candidates.append((a, b))

        return candidates

    def _has_conflict(self, skill_id_a: str, skill_id_b: str) -> bool:
        skill_a = self.skill_registry.get(skill_id_a, {})
        skill_b = self.skill_registry.get(skill_id_b, {})

        resources_a = set(skill_a.get("resources", []))
        resources_b = set(skill_b.get("resources", []))

        if resources_a and resources_b and resources_a & resources_b:
            return True

        if skill_a.get("category") == skill_b.get("category"):
            return False

        return False

    def _find_redundant_skills(self, skill_ids: List[str]) -> List[str]:
        redundant: List[str] = []

        for i, sid_a in enumerate(skill_ids):
            skill_a = self.skill_registry.get(sid_a, {})
            for sid_b in skill_ids[i + 1:]:
                skill_b = self.skill_registry.get(sid_b, {})
                similarity = self._calculate_skill_similarity(skill_a, skill_b)
                if similarity > 0.8:
                    if sid_a not in redundant:
                        redundant.append(sid_a)

        return redundant

    def _calculate_skill_similarity(
        self,
        skill_a: Dict[str, Any],
        skill_b: Dict[str, Any],
    ) -> float:
        tags_a = set(skill_a.get("tags", []))
        tags_b = set(skill_b.get("tags", []))

        if not tags_a and not tags_b:
            return 0.0

        intersection = tags_a & tags_b
        union = tags_a | tags_b

        if not union:
            return 0.0

        tag_similarity = len(intersection) / len(union)

        category_similarity = 1.0 if skill_a.get("category") == skill_b.get("category") else 0.0

        return 0.6 * tag_similarity + 0.4 * category_similarity

    def _suggest_missing_links(self, skill_ids: List[str]) -> List[str]:
        suggestions: List[str] = []

        for i, sid_a in enumerate(skill_ids):
            skill_a = self.skill_registry.get(sid_a, {})
            for sid_b in skill_ids[i + 1:]:
                skill_b = self.skill_registry.get(sid_b, {})

                deps_a = set(skill_a.get("dependencies", []))
                deps_b = set(skill_b.get("dependencies", []))

                if sid_a not in deps_b and sid_b not in deps_a:
                    overlap = len(set(skill_a.get("tags", [])) & set(skill_b.get("tags", [])))
                    if overlap >= 2:
                        suggestions.append(f"{sid_a} <-> {sid_b} (shared tags)")

        return suggestions