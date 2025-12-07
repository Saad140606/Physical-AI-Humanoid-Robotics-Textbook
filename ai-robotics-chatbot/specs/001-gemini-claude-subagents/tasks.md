# Task Breakdown: Multi-Provider LLM & Subagent Framework

**Feature**: `001-gemini-claude-subagents`  
**Plan Reference**: `specs/001-gemini-claude-subagents/plan.md`  
**Total Estimated Hours**: ~4.5 hours  

## Task List

### T-001: Install Dependencies & Validate Config
**Estimated Time**: 15 min  
**Priority**: Critical  
**Acceptance Criteria**:
- [ ] `google-generativeai` installed via pip
- [ ] `config.py` includes `llm_provider`, `claude_api_key`, `gemini_api_key` fields
- [ ] `.env` updated with `LLM_PROVIDER=google`, `GEMINI_API_KEY=<key>`, `CLAUDE_API_KEY=<key>`
- [ ] `python -c "import google.generativeai; import anthropic; print('OK')"` succeeds
- [ ] `python -c "from config import settings; print(settings.llm_provider)"` returns active provider

**Owner**: Platform  
**Dependencies**: None

---

### T-002: Implement GeminiAdapter in llm_service.py
**Estimated Time**: 45 min  
**Priority**: High  
**Acceptance Criteria**:
- [ ] New `GeminiAdapter` class created with `generate_response(prompt, history)` method
- [ ] Adapter attempts to call `genai.generate_text()` or `genai.chat.completions.create()`
- [ ] On `RateLimitError` or API error, adapter raises custom exception
- [ ] Adapter has `test_connection()` method that returns `{"status": "ok", "model": "gemini-pro"}`
- [ ] Adapter respects `max_tokens`, `temperature` from config

**Owner**: Platform  
**Dependencies**: T-001  
**Notes**: Model name may vary; acceptable names: `gemini-pro`, `gemini-1.5-pro`, `gemini-pro-vision`

---

### T-003: Implement ClaudeAdapter in llm_service.py
**Estimated Time**: 45 min  
**Priority**: High  
**Acceptance Criteria**:
- [ ] New `ClaudeAdapter` class created with `generate_response(prompt, history)` method
- [ ] Adapter calls `anthropic.Anthropic(api_key=...).messages.create(model="claude-3-sonnet-20240229", ...)`
- [ ] On `RateLimitError` or API error, adapter raises custom exception
- [ ] Adapter has `test_connection()` method that returns `{"status": "ok", "model": "claude-3-sonnet"}`
- [ ] Adapter respects `max_tokens`, `temperature` from config

**Owner**: Platform  
**Dependencies**: T-001  
**Notes**: Model can be configurable; default `claude-3-sonnet-20240229`

---

### T-004: Refactor RAGChatService for Multi-Provider Support
**Estimated Time**: 30 min  
**Priority**: High  
**Acceptance Criteria**:
- [ ] `RAGChatService.__init__()` initializes adapter based on `settings.llm_provider`
- [ ] If provider not recognized, defaults to `openai`
- [ ] `RAGChatService.generate_response()` calls active adapter first, then fallback chain
- [ ] Fallback order: Active → OpenAI → Local Knowledge Base
- [ ] Errors logged but not raised (graceful degradation)
- [ ] Response includes metadata: `{"response": "...", "provider_used": "gemini"}`

**Owner**: Platform  
**Dependencies**: T-002, T-003

---

### T-005: Create Subagent Framework (agents.py)
**Estimated Time**: 1 hour  
**Priority**: Medium  
**Acceptance Criteria**:
- [ ] New file `app/agents.py` created with `SubagentBase` abstract class
- [ ] `SubagentBase` has methods: `invoke(query, context)`, `metadata()`, `test()`
- [ ] Three subagents implemented:
  - `DocumentSearchAgent`: searches vector DB, returns top-k documents with scores
  - `CodeAgent`: generates code snippets for robotics problems (template-based)
  - `CitationAgent`: formats sources with footnotes and bibliography
- [ ] `SubagentRegistry` class with `register(subagent)`, `get(name)`, `list_all()` methods
- [ ] `@subagent` decorator for easy registration
- [ ] Each subagent has `invoke(query, context)` returning `{"status": "ok", "result": {...}, "metadata": {}}`

**Owner**: Platform  
**Dependencies**: T-004, existing `app/vector_db.py`

---

### T-006: Extend chat.py Routes for Subagent Support
**Estimated Time**: 45 min  
**Priority**: Medium  
**Acceptance Criteria**:
- [ ] `ChatRequest` model updated with optional `use_agent: Optional[str] = None`
- [ ] `ChatResponse` model updated with `agent_used: Optional[str] = None`
- [ ] `/api/chat/query` POST handler checks for `use_agent` field
- [ ] If `use_agent` present, route request to `SubagentRegistry.get(use_agent).invoke(query, ...)`
- [ ] Response includes `agent_used` field
- [ ] If subagent fails or not found, fallback to default LLM behavior
- [ ] No 500 errors; all errors return 200 with `{"error": "message", "response": "fallback"}`

**Owner**: API  
**Dependencies**: T-005

---

### T-007: Create SubagentList Endpoint (Optional)
**Estimated Time**: 20 min  
**Priority**: Low  
**Acceptance Criteria**:
- [ ] New endpoint `GET /api/agents` returns list of available subagents
- [ ] Response format: `{"agents": [{"name": "document_search", "description": "..."}, ...]}`
- [ ] Can be used by frontend for dynamic agent selection UI

**Owner**: API  
**Dependencies**: T-005

---

### T-008: Update Health Endpoint
**Estimated Time**: 15 min  
**Priority**: Medium  
**Acceptance Criteria**:
- [ ] `/api/health` response includes `llm_provider` field
- [ ] Response format: `{"status": "healthy", "llm_provider": "google", "agents_available": 3, "vector_db": "connected"}`
- [ ] Adapters tested at startup; any failures logged but don't prevent server start

**Owner**: API  
**Dependencies**: T-004

---

### T-009: Fallback & Error Handling Tests
**Estimated Time**: 30 min  
**Priority**: High  
**Acceptance Criteria**:
- [ ] Manually test with invalid/expired API keys; system returns graceful fallback
- [ ] Test network timeout simulation; system retries 3x then falls back
- [ ] Test nonexistent subagent name; system logs warning and uses default LLM
- [ ] All test scenarios return 200 status (no 500 errors)
- [ ] Response quality acceptable (fallback knowledge base or cached response)

**Owner**: QA  
**Dependencies**: T-004, T-005, T-006

---

### T-010: Integration Test & Documentation
**Estimated Time**: 45 min  
**Priority**: High  
**Acceptance Criteria**:
- [ ] Start backend with `LLM_PROVIDER=google`; verify `/api/health` reports `gemini`
- [ ] POST to `/api/chat/query` with `{"query": "What is a robot?"}` → receives Gemini response (or fallback)
- [ ] POST with `{"query": "...", "use_agent": "document_search"}` → receives documents with agent metadata
- [ ] Switch to `LLM_PROVIDER=claude` in `.env`; restart backend; verify `/api/health` reports `claude`
- [ ] All 3 providers tested (openai, google, claude)
- [ ] Response time < 5 seconds for queries (excluding network latency)
- [ ] Documentation updated: README.md includes "Configuring LLM Providers" section

**Owner**: QA + Docs  
**Dependencies**: T-001 through T-008

---

### T-011: Create PHR Record (Governance)
**Estimated Time**: 15 min  
**Priority**: Medium  
**Acceptance Criteria**:
- [ ] New file created: `history/prompts/general/001-multi-provider-llm-subagents.general.prompt.md`
- [ ] YAML front matter includes: `id`, `title`, `stage`, `date`, `feature`, `status`, `files_modified`
- [ ] Markdown body contains:
  - User request verbatim
  - Implementation summary (what was done)
  - Key decisions made
  - Testing outcomes
  - Link to feature spec
- [ ] File follows format in CLAUDE.md

**Owner**: Docs  
**Dependencies**: T-010

---

## Task Dependencies Graph

```
T-001 (Install)
├── T-002 (GeminiAdapter)
│   └── T-004 (MultiProvider)
│       └── T-006 (SubagentRoutes)
│           └── T-010 (Integration)
│               └── T-011 (PHR)
├── T-003 (ClaudeAdapter)
│   └── T-004 (MultiProvider) [same as above]
└── T-009 (ErrorHandling)
    └── T-010 (Integration) [same as above]

T-005 (SubagentFramework)
├── T-006 (SubagentRoutes) [same as above]
├── T-007 (AgentList) [optional]
└── T-008 (HealthEndpoint)
    └── T-010 (Integration) [same as above]
```

## Sprint Allocation (Recommended)

**Sprint 1 (Config & Setup)**: T-001, T-008  
**Sprint 2 (Adapters & Integration)**: T-002, T-003, T-004  
**Sprint 3 (Subagents)**: T-005, T-006, T-007  
**Sprint 4 (Testing & Docs)**: T-009, T-010, T-011  

## Rollout Checklist

- [ ] All tasks marked complete
- [ ] No pending GitHub issues related to this feature
- [ ] Code reviewed and approved by 1+ team members
- [ ] All endpoints tested in Postman/curl
- [ ] PHR record filed
- [ ] README updated with new feature documentation
- [ ] Feature branch merged to main
- [ ] Tag created: `v1.0-multiprovider-llm`
