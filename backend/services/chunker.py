"""Granular chunking helpers for section trees."""
from __future__ import annotations

from ..models import ParsedObject, SectionNode

__all__ = ["compute_section_spans"]


def compute_section_spans(root: SectionNode, objects: list[ParsedObject]) -> dict[str, list[str]]:
    """Return ordered object identifiers for every section in the tree.

    The function enforces non-overlapping assignments across leaf sections using
    the deterministic tie-breaker described in the phase plan. Parent sections
    receive the ordered concatenation of their descendant leaf chunks.
    """

    ordered_objects = list(objects)
    object_index: dict[str, int] = {obj.object_id: idx for idx, obj in enumerate(ordered_objects)}

    leaf_nodes: list[SectionNode] = []
    all_nodes: list[SectionNode] = []

    def _collect(node: SectionNode) -> None:
        all_nodes.append(node)
        if not node.children:
            leaf_nodes.append(node)
        for child in node.children:
            _collect(child)

    _collect(root)

    leaf_ranges: dict[str, tuple[int, int]] = {}
    for leaf in leaf_nodes:
        start_id = leaf.span.start_object
        end_id = leaf.span.end_object
        if start_id is None or end_id is None:
            continue
        start_index = object_index.get(start_id)
        end_index = object_index.get(end_id)
        if start_index is None or end_index is None:
            continue
        low, high = sorted((start_index, end_index))
        leaf_ranges[leaf.section_id] = (low, high)

    leaf_chunks: dict[str, list[str]] = {leaf.section_id: [] for leaf in leaf_nodes}

    for index, obj in enumerate(ordered_objects):
        candidates: list[tuple[int, int, str, SectionNode]] = []
        for leaf in leaf_nodes:
            span = leaf_ranges.get(leaf.section_id)
            if span is None:
                continue
            start_idx, end_idx = span
            if index < start_idx or index > end_idx:
                continue
            distance = index - start_idx
            candidates.append((distance, leaf.depth, leaf.section_id, leaf))
        if not candidates:
            continue
        _, _, _, chosen_leaf = min(candidates, key=lambda item: (item[0], item[1], item[2]))
        leaf_chunks[chosen_leaf.section_id].append(obj.object_id)

    result: dict[str, list[str]] = {}

    def _build(node: SectionNode) -> list[str]:
        if not node.children:
            chunk = list(leaf_chunks.get(node.section_id, []))
            result[node.section_id] = chunk
            return list(chunk)
        aggregate: list[str] = []
        for child in node.children:
            aggregate.extend(_build(child))
        chunk_copy = list(aggregate)
        result[node.section_id] = chunk_copy
        return aggregate

    _build(root)

    for node in all_nodes:
        result.setdefault(node.section_id, [])

    return result
