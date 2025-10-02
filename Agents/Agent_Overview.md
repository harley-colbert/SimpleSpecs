# Simplespecs Agents — Overview
**Date:** 2025-10-02

This package provides copy‑paste **Agent files** (prompts) for automating each phase of the UNO‑less Simplespecs plan with a MinerU toggle. Use these with ChatGPT/Codex or similar “code agent” tools.

## Files
- `Agent_Overview.md` — this document.
- `Agent_P0.md` — Phase 0 (Architecture & Contracts).
- `Agent_P1.md` — Phase 1 (Upload & Parsing; Native + MinerU).
- `Agent_P2.md` — Phase 2 (Header Discovery / LLM).
- `Agent_P3.md` — Phase 3 (Granular Chunking).
- `Agent_P4.md` — Phase 4 (Spec Extraction Loop).
- `Agent_P5.md` — Phase 5 (QA, Export, CI).

## Inputs expected by agents
- Plans: `plan_docs/overview.md`, `plan_docs/phase_P{N}_*.md`
- Final stubs: `finalstubs/finalstubs_latest.json`, `finalstubs/finalstubs_P{N}.json`
- Repo root: your working directory should be the project root.

## Global guardrails
1. Do not create files outside `finalstubs_P{N}.json` for the target phase.
2. Preserve exact paths and names; match function signatures from the stubs.
3. Keep code runnable under a normal Python **venv**; **no UNO/pyuno** usage.
4. For networked features in early phases, use **mock implementations**.
5. Every file must have clear docstrings, type hints, and minimal working logic.
