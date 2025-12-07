# Implementation Plan: Multi-Provider LLM & Subagent Framework

**Feature Branch**: `001-gemini-claude-subagents`  
**Feature Spec**: `specs/001-gemini-claude-subagents/spec.md`  
**Created**: 2025-12-07  
**Status**: Active

## Technical Context & Scope

### In Scope
- Add `LLM_PROVIDER` and provider-specific API keys to `config.py`
- Implement `GeminiAdapter` and `ClaudeAdapter` in `app/llm_service.py`
- Create `app/agents.py` with subagent registry, dispatcher, and 3 sample subagents
- Update `app/routes/chat.py` to support `use_agent` field
- Implement fallback logic for all providers
- Update `/api/health` to report active provider
- Add provider selection via environment variables (no code changes required for switching)

### Out of Scope
- Deployment to production (Docker, cloud platforms)
- Monitoring and logging infrastructure
- Fine-tuning or training custom models
- Real-time performance optimization

### Dependencies
- `google-generativeai` Python SDK (install)
- `anthropic` Python SDK (already installed)
- Existing `app/llm_service.py`, `app/vector_db.py`, `config.py`
- Qdrant cloud setup (for vector search subagent)

## Implementation Phases

### Phase 1: Configuration & Setup (Est. 30 min)
- Update `config.py` to include `LLM_PROVIDER`, `CLAUDE_API_KEY`, `GEMINI_API_KEY`
- Install `google-generativeai` via pip
- Update `.env` with new keys

### Phase 2: LLM Adapters (Est. 1.5 hours)
- Refactor `app/llm_service.py` to add `GeminiAdapter` and `ClaudeAdapter`
- Implement provider-aware initialization in `RAGChatService.__init__()`
- Add retry logic and fallback handling for each provider
- Test each adapter independently

### Phase 3: Subagent Framework (Est. 1 hour)
- Create `app/agents.py` with:
  - `SubagentBase` abstract class
  - `DocumentSearchAgent`, `CodeAgent`, `CitationAgent` implementations
  - `SubagentRegistry` for discovery and dispatch
- Implement `@subagent` decorator for easy registration

### Phase 4: Route Integration (Est. 45 min)
- Update `app/routes/chat.py` to:
  - Parse `use_agent` field from request
  - Route to appropriate subagent if specified
  - Include agent metadata in response
- Create optional `app/routes/agents.py` for direct agent invocation

### Phase 5: Testing & Validation (Est. 1 hour)
- Start backend with `LLM_PROVIDER=google`
- Test `/api/health` response
- POST sample queries to `/api/chat/query`
- Test subagent invocation with `use_agent=document_search`
- Test fallback behavior (e.g., invalid API key)
- Verify response format and latency

## Risk Analysis & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Gemini/Claude API quota exceeded | Medium | High | Implement rate limiting, fallback to OpenAI |
| Network timeout on API calls | Medium | Medium | Add 3-attempt retry with exponential backoff |
| Subagent latency > 5 sec | Low | Medium | Cache results, implement async execution |
| Configuration errors | Low | Low | Validate config on startup, print detailed errors |

## Definition of Done

- ✅ All adapters (OpenAI, Gemini, Claude) successfully return responses
- ✅ Subagent framework initialized and at least 1 subagent available
- ✅ `/api/health` reports correct provider and agent count
- ✅ Fallback logic tested and working
- ✅ No 500 errors on invalid inputs (graceful 200 with error message)
- ✅ PHR created documenting implementation decisions
- ✅ All specs and tasks marked complete
