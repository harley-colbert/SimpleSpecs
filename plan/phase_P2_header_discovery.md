# Phase P2 — Header Discovery (LLM)
**Outcome:** LLM-derived nested headers into `SectionNode` tree; persisted and viewable.

## Tasks
1. LLM adapters (OpenRouter/llama.cpp) share `complete()` interface.
2. Build headers prompt; handle truncation warnings if text > token budget.
3. Parse nested list variants (bullets, numbered, mixed) into `SectionNode` tree; store and expose via routes.
4. UI tree viewer.

## Acceptance
- Trees match LLM output on fixtures (spot-checked).