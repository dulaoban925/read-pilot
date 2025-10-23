# Tasks: Core Reading Experience

**Input**: Design documents from `/specs/001-core-reading-experience/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the feature specification, so test tasks are EXCLUDED per the Task Generation Rules.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/app/`, `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend project structure in backend/ directory
- [x] T002 Initialize Poetry project with pyproject.toml in backend/
- [x] T003 [P] Create frontend project with Next.js 15 in frontend/ directory
- [x] T004 [P] Setup Docker Compose configuration in docker-compose.yml
- [x] T005 [P] Create environment variables template files (.env.example in both backend and frontend)
- [x] T006 [P] Configure backend linting tools (Ruff) in backend/pyproject.toml
- [x] T007 [P] Configure frontend linting tools (ESLint, Prettier) in frontend/
- [ ] T008 Create shared Docker configuration files in shared/docker/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation

- [x] T009 Install core backend dependencies (FastAPI, SQLAlchemy, Celery) via Poetry in backend/
- [x] T010 [P] Setup database configuration in backend/app/db/session.py
- [x] T011 [P] Setup application settings in backend/app/core/config.py
- [x] T012 [P] Create base SQLAlchemy model class in backend/app/models/base.py
- [x] T013 Initialize Alembic for database migrations in backend/alembic/
- [x] T014 [P] Create FastAPI app instance and main entry point in backend/app/main.py
- [x] T015 [P] Setup CORS middleware in backend/app/main.py
- [x] T016 [P] Setup structured logging with structlog in backend/app/utils/logger.py
- [x] T017 [P] Create error handling middleware (global exception handlers) in backend/app/main.py
- [x] T018 [P] Create API dependency injection utilities in backend/app/core/deps.py
- [x] T019 Setup Celery app configuration in backend/app/tasks/celery_app.py
- [x] T020 [P] Setup Redis connection for caching in backend/app/core/cache.py
- [x] T021 [P] Setup ChromaDB client configuration in backend/app/core/vector_db.py

### Backend - Authentication & Authorization

- [x] T022 Create User model in backend/app/models/user.py
- [x] T023 Create User schema (Pydantic) in backend/app/schemas/auth.py
- [x] T024 Implement password hashing utilities in backend/app/core/security.py
- [x] T025 Implement JWT token utilities in backend/app/core/security.py
- [x] T026 Create authentication service in backend/app/services/auth_service.py
- [x] T027 Create authentication endpoints in backend/app/api/v1/auth.py
- [x] T028 Create get_current_user dependency in backend/app/core/deps.py
- [x] T029 Generate initial database migration for User table in backend/alembic/versions/

### Backend - Core Abstractions

- [x] T030 [P] Create document parser base class in backend/app/core/document_parser/base.py
- [x] T031 [P] Create AI provider base class in backend/app/core/ai/base.py
- [x] T032 [P] Create file storage base class in backend/app/utils/file_handler.py
- [x] T033 [P] Create cache service in backend/app/core/cache.py

### Frontend Foundation

- [x] T034 Install core frontend dependencies (React 19, Zustand, Axios) in frontend/
- [x] T035 [P] Setup Tailwind CSS 4.0 configuration in frontend/tailwind.config.js
- [x] T036 [P] Create global styles in frontend/src/styles/globals.css
- [x] T037 [P] Setup Axios client with interceptors in frontend/src/lib/api.ts
- [x] T038 [P] Setup TanStack Query provider in frontend/src/app/layout.tsx
- [x] T039 [P] Create API types definitions in frontend/src/types/api.ts
- [x] T040 [P] Create auth store with Zustand in frontend/src/stores/authStore.ts
- [x] T041 [P] Create auth utility functions in frontend/src/lib/auth.ts
- [x] T042 [P] Create common UI components (Button, Input, Card) from Radix UI in frontend/src/components/ui/
- [x] T043 Create root layout with header/footer in frontend/src/app/layout.tsx
- [x] T044 [P] Create Header component in frontend/src/components/layout/Header.tsx
- [x] T045 [P] Create authentication pages (login, register) in frontend/src/app/auth/

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Document Upload and Processing (Priority: P1) 🎯 MVP

**Goal**: Users can upload documents (PDF, EPUB, DOCX, Markdown), and the system extracts text, chunks it, generates embeddings, and stores them in a vector database for semantic search.

**Independent Test**: Upload a sample document and verify that: (1) upload completes successfully, (2) text is extracted correctly, (3) document appears in user's library with correct metadata, and (4) processing completes without errors.

### Backend - Data Models

- [x] T046 [P] [US1] Create Document model in backend/app/models/document.py
- [x] T047 [P] [US1] Create DocumentChunk model in backend/app/models/document_chunk.py
- [x] T048 [P] [US1] Create ReadingHistory model (ReadingSession) in backend/app/models/reading_session.py
- [x] T049 [US1] Generate database migration for Document, DocumentChunk, ReadingHistory tables in backend/alembic/versions/

### Backend - Schemas

- [x] T050 [P] [US1] Create document schemas (Pydantic) in backend/app/schemas/document.py

### Backend - Document Parsers

- [x] T051 [P] [US1] Implement PDF parser using PyMuPDF in backend/app/core/document_parser/pdf_parser.py
- [x] T052 [P] [US1] Implement EPUB parser using ebooklib in backend/app/core/document_parser/epub_parser.py
- [x] T053 [P] [US1] Implement DOCX parser using python-docx in backend/app/core/document_parser/docx_parser.py
- [x] T054 [P] [US1] Implement Markdown/Text parser in backend/app/core/document_parser/text_parser.py
- [x] T055 [US1] Create parser factory with format detection in backend/app/core/document_parser/**init**.py

### Backend - Text Processing

- [x] T056 [US1] Implement text chunker using LangChain in backend/app/core/text_chunker.py
- [x] T057 [US1] Implement embedding generator using OpenAI in backend/app/core/embedding_generator.py
- [x] T058 [US1] Create vector database service for ChromaDB in backend/app/core/vector_db.py

### Backend - Storage

- [x] T059 [P] [US1] Implement local file storage in backend/app/utils/file_handler.py
- [x] T060 [P] [US1] Implement S3-compatible file storage in backend/app/utils/file_handler.py

### Backend - Services

- [x] T061 [US1] Implement document service with upload/list/get/delete in backend/app/services/document_service.py

### Backend - Celery Tasks

- [x] T062 [US1] Create document processing Celery task in backend/app/tasks/document_processing.py
- [x] T063 [US1] Create embedding generation Celery task in backend/app/tasks/embedding_tasks.py

### Backend - API Endpoints

- [x] T064 [US1] Implement POST /api/v1/documents (upload) in backend/app/api/v1/documents.py
- [x] T065 [US1] Implement GET /api/v1/documents (list) in backend/app/api/v1/documents.py
- [x] T066 [US1] Implement GET /api/v1/documents/{id} (get detail) in backend/app/api/v1/documents.py
- [x] T067 [US1] Implement DELETE /api/v1/documents/{id} in backend/app/api/v1/documents.py
- [x] T068 [US1] Implement GET /api/v1/documents/{id}/download in backend/app/api/v1/documents.py

### Frontend - Types & Stores

- [x] T069 [P] [US1] Create document type definitions in frontend/src/types/document.ts
- [x] T070 [US1] Create document store with Zustand in frontend/src/stores/documentStore.ts

### Frontend - Components

- [x] T071 [P] [US1] Create DocumentUploader component with drag-and-drop in frontend/src/components/document/DocumentUploader.tsx
- [x] T072 [P] [US1] Create DocumentList component with status indicators in frontend/src/components/document/DocumentList.tsx
- [x] T073 [P] [US1] Create DocumentCard component in frontend/src/components/document/DocumentCard.tsx
- [x] T074 [P] [US1] Create ProcessingStatusBadge component in frontend/src/components/document/ProcessingStatusBadge.tsx

### Frontend - Pages

- [x] T075 [US1] Create documents library page in frontend/src/app/documents/page.tsx
- [x] T076 [US1] Create document details page in frontend/src/app/documents/[id]/page.tsx

### Frontend - API Hooks

- [x] T077 [US1] Create useDocuments hook (TanStack Query) in frontend/src/lib/hooks/useDocuments.ts
- [x] T078 [US1] Create useUploadDocument mutation hook in frontend/src/lib/hooks/useDocuments.ts
- [x] T079 [US1] Create useDeleteDocument mutation hook in frontend/src/lib/hooks/useDocuments.ts

### Error Handling & Validation

- [x] T080 [US1] Add file validation (size, format, page count) in backend/app/services/document_service.py
- [x] T081 [US1] Add error handling for parsing failures in backend/app/tasks/document_processing.py
- [x] T082 [US1] Add rate limiting for document uploads in backend/app/api/v1/documents.py
- [x] T083 [US1] Add frontend validation for file size and format in DocumentUploader component

**Checkpoint**: User Story 1 should be fully functional - users can upload documents and see processing status

---

## Phase 4: User Story 2 - AI-Powered Document Summarization (Priority: P2)

**Goal**: Users can request AI-generated summaries of processed documents to quickly understand key points, insights, and concepts.

**Independent Test**: Upload a document (using User Story 1), request a summary, and verify that: (1) summary is generated within 10 seconds, (2) summary includes abstract, key insights, and main concepts, (3) summaries are cached for quick retrieval.

### Backend - Data Models

- [x] T084 [US2] Create Summary model (AISummary) in backend/app/models/ai_summary.py
- [x] T085 [US2] Generate database migration for Summary table in backend/alembic/versions/

### Backend - Schemas

- [x] T086 [P] [US2] Create summary schemas (Pydantic) in backend/app/schemas/document.py

### Backend - AI Providers

- [x] T087 [P] [US2] Implement OpenAI provider for summarization in backend/app/core/ai/openai_service.py
- [x] T088 [P] [US2] Implement Anthropic provider for summarization in backend/app/core/ai/anthropic_service.py
- [x] T089 [US2] Create AI service factory with fallback logic in backend/app/services/ai_service.py

### Backend - Services

- [x] T090 [US2] Extend document service with summary methods in backend/app/services/document_service.py
- [x] T091 [US2] Implement summary caching with Redis in backend/app/services/cache_service.py

### Backend - Celery Tasks

- [x] T092 [US2] Create summary generation Celery task in backend/app/tasks/document_processing.py

### Backend - API Endpoints

- [x] T093 [US2] Implement POST /api/v1/documents/{id}/summarize in backend/app/api/v1/documents.py
- [x] T094 [US2] Implement GET /api/v1/documents/{id}/summary in backend/app/api/v1/documents.py

### Frontend - Components

- [x] T095 [P] [US2] Create SummaryDisplay component in frontend/src/components/document/SummaryDisplay.tsx
- [x] T096 [P] [US2] Create SummaryControls component (depth selection) in frontend/src/components/document/SummaryControls.tsx
- [x] T097 [P] [US2] Create LoadingSummary skeleton component in frontend/src/components/document/LoadingSummary.tsx

### Frontend - Pages & Integration

- [x] T098 [US2] Add summary section to document details page in frontend/src/app/documents/[id]/page.tsx

### Frontend - API Hooks

- [x] T099 [US2] Create useSummary hook (TanStack Query) in frontend/src/lib/hooks/useSummary.ts
- [x] T100 [US2] Create useGenerateSummary mutation hook in frontend/src/lib/hooks/useSummary.ts

### Error Handling

- [x] T101 [US2] Add graceful degradation when AI services unavailable in backend/app/services/ai_service.py
- [x] T102 [US2] Add retry logic with exponential backoff in backend/app/core/ai/qwen_service.py (using tenacity @retry decorator)
- [x] T103 [US2] Add frontend error handling for AI failures in SummaryDisplay component

### Data Transformation

- [x] T104 [US2] Implement SummaryResponse.from_ai_summary() method in backend/app/schemas/document.py (converts AISummary model's JSON fields to flat response structure)
- [x] T105 [US2] Update GET /api/v1/documents/{id}/summary endpoint to use from_ai_summary() converter in backend/app/api/v1/documents.py

**Data Flow**: AISummary (DB: content JSON) → SummaryResponse.from_ai_summary() → API JSON → Frontend Summary interface

### Multi-AI Provider Support (2025-10-23 完成)

- [x] T106 [US2] Implement QwenEmbeddingService with text-embedding-v3 in backend/app/core/ai/qwen_service.py
- [x] T107 [US2] Update get_embedding_service() to follow PRIMARY_AI_PROVIDER in backend/app/core/ai/__init__.py
- [x] T108 [US2] Update embedding_tasks.py to dynamically get model name from service in backend/app/tasks/embedding_tasks.py
- [x] T109 [US2] Fix summary_service.py to use document_parser_factory for real content extraction in backend/app/services/summary_service.py
- [x] T110 [US2] Update .env.example with multi-provider configuration guide
- [x] T111 [US2] Update plan.md to document multi-provider architecture and mark Extensibility principle as resolved
- [x] T116 [US2] Fix get_embedding_service() to follow PRIMARY_AI_PROVIDER (prevent Qwen LLM with OpenAI Embedding mismatch)

**AI Provider Architecture**:
- **LLM Services**: OpenAI (gpt-4o-mini), Anthropic (claude-3-5-sonnet), Qwen (qwen-max/plus/turbo/flash)
- **Embedding Services**: 跟随 PRIMARY_AI_PROVIDER 配置
  - PRIMARY_AI_PROVIDER=qwen → Qwen Embedding (text-embedding-v3)
  - PRIMARY_AI_PROVIDER=openai → OpenAI Embedding (text-embedding-3-small)
  - PRIMARY_AI_PROVIDER=anthropic → 降级到 OpenAI 或 Qwen (Anthropic 不支持 Embedding)
- **Configuration**: 通过环境变量 `PRIMARY_AI_PROVIDER`, `FALLBACK_AI_PROVIDER`, `QWEN_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` 配置
- **Consistency**: Embedding 服务与 LLM 服务保持一致,避免混用不同提供商

### Frontend API Refactoring (2025-10-23 完成)

- [x] T112 [US2] Refactor useSummary.ts to use api.get() instead of apiClient in frontend/src/lib/hooks/useSummary.ts
- [x] T113 [US2] Refactor useGenerateSummary.ts to use api.post() instead of apiClient in frontend/src/lib/hooks/useGenerateSummary.ts
- [x] T114 [US2] Fix Select component to properly display and update selected value in frontend/src/components/ui/Select.tsx
- [x] T115 [US2] Change default summary depth to 'brief' in SummaryControls component

**Checkpoint**: User Stories 1 AND 2 should both work independently - users can upload documents and generate summaries

---

## Phase 5: User Story 3 - Context-Aware Q&A (Priority: P3)

**Goal**: Users can ask questions about document content in natural language and receive accurate answers with citations. The system maintains conversation history across sessions.

**Independent Test**: Upload a document, ask specific questions, and verify that: (1) answers are generated within 5 seconds, (2) answers are contextually accurate, (3) source citations reference correct pages/sections, (4) conversation history persists across page refreshes.

### Backend - Data Models

- [x] T104 [P] [US3] Create ChatSession model in backend/app/models/chat_session.py
- [x] T105 [P] [US3] Create Message model in backend/app/models/message.py
- [ ] T106 [US3] Generate database migration for ChatSession, Message tables in backend/alembic/versions/

### Backend - Schemas

- [ ] T107 [P] [US3] Create chat schemas (Pydantic) in backend/app/schemas/chat.py

### Backend - Services

- [ ] T108 [US3] Extend AI service with Q&A methods in backend/app/services/ai_service.py
- [ ] T109 [US3] Extend vector service with semantic search in backend/app/services/vector_service.py
- [ ] T110 [US3] Create chat service with session management in backend/app/services/chat_service.py

### Backend - API Endpoints

- [ ] T111 [US3] Implement POST /api/v1/chat/sessions in backend/app/api/v1/chat.py
- [ ] T112 [US3] Implement GET /api/v1/chat/sessions in backend/app/api/v1/chat.py
- [ ] T113 [US3] Implement GET /api/v1/chat/sessions/{id} in backend/app/api/v1/chat.py
- [ ] T114 [US3] Implement DELETE /api/v1/chat/sessions/{id} in backend/app/api/v1/chat.py
- [ ] T115 [US3] Implement POST /api/v1/chat/sessions/{id}/messages in backend/app/api/v1/chat.py
- [ ] T116 [US3] Implement GET /api/v1/chat/sessions/{id}/messages in backend/app/api/v1/chat.py

### Frontend - Types & Stores

- [ ] T117 [P] [US3] Create chat type definitions in frontend/src/types/chat.ts
- [ ] T118 [US3] Create chat store with Zustand in frontend/src/stores/chatStore.ts

### Frontend - Components

- [ ] T119 [P] [US3] Create ChatInterface component in frontend/src/components/chat/ChatInterface.tsx
- [ ] T120 [P] [US3] Create MessageList component in frontend/src/components/chat/MessageList.tsx
- [ ] T121 [P] [US3] Create MessageInput component in frontend/src/components/chat/MessageInput.tsx
- [ ] T122 [P] [US3] Create MessageBubble component with citations in frontend/src/components/chat/MessageBubble.tsx
- [ ] T123 [P] [US3] Create SuggestedQuestions component in frontend/src/components/chat/SuggestedQuestions.tsx

### Frontend - Pages

- [ ] T124 [US3] Create chat session page in frontend/src/app/chat/[sessionId]/page.tsx

### Frontend - API Hooks

- [ ] T125 [US3] Create useChatSessions hook in frontend/src/lib/hooks/useChat.ts
- [ ] T126 [US3] Create useMessages hook in frontend/src/lib/hooks/useChat.ts
- [ ] T127 [US3] Create useSendMessage mutation hook in frontend/src/lib/hooks/useChat.ts

### Context & Citations

- [ ] T128 [US3] Implement conversation context management in backend/app/services/chat_service.py
- [ ] T129 [US3] Implement source citation extraction in backend/app/services/ai_service.py
- [ ] T130 [US3] Add follow-up question suggestions in backend/app/services/ai_service.py

### Error Handling

- [ ] T131 [US3] Add handling for empty search results in backend/app/services/vector_service.py
- [ ] T132 [US3] Add conversation history limits and cleanup in backend/app/services/chat_service.py

**Checkpoint**: All user stories should now be independently functional - complete MVP with upload, summarization, and Q&A

---

## Phase 6: User Profile & Statistics

**Goal**: Users can view their profile, update preferences, and see reading statistics.

### Backend - API Endpoints

- [ ] T133 [P] Implement GET /api/v1/users/me in backend/app/api/v1/users.py
- [ ] T134 [P] Implement PUT /api/v1/users/me in backend/app/api/v1/users.py
- [ ] T135 Implement GET /api/v1/users/me/stats in backend/app/api/v1/users.py

### Backend - Services

- [ ] T136 Create user service with profile and stats methods in backend/app/services/user_service.py
- [ ] T137 Implement reading history tracking in backend/app/services/document_service.py

### Backend - Schemas

- [ ] T138 [P] Create user schemas (Pydantic) in backend/app/schemas/user.py

### Frontend - Components

- [ ] T139 [P] Create UserProfile component in frontend/src/components/user/UserProfile.tsx
- [ ] T140 [P] Create ReadingStats component in frontend/src/components/user/ReadingStats.tsx
- [ ] T141 [P] Create PreferencesForm component in frontend/src/components/user/PreferencesForm.tsx

### Frontend - Pages

- [ ] T142 Create user profile page in frontend/src/app/profile/page.tsx

### Frontend - API Hooks

- [ ] T143 Create useUser hook in frontend/src/lib/hooks/useUser.ts
- [ ] T144 Create useUpdateUser mutation hook in frontend/src/lib/hooks/useUser.ts

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Performance Optimization

- [ ] T145 [P] Add database indexes per data-model.md in backend/alembic/versions/
- [ ] T146 [P] Add database constraints and triggers per data-model.md in backend/alembic/versions/
- [ ] T147 [P] Optimize vector search queries in backend/app/services/vector_service.py
- [ ] T148 [P] Add response caching for frequently accessed endpoints in backend/app/api/v1/
- [ ] T149 [P] Optimize frontend bundle size with code splitting in frontend/next.config.js

### Monitoring & Logging

- [ ] T150 [P] Add Prometheus metrics endpoints in backend/app/main.py
- [ ] T151 [P] Add request logging middleware in backend/app/middleware/logging.py
- [ ] T152 [P] Setup Sentry error tracking in frontend/src/app/layout.tsx

### Security Hardening

- [ ] T153 [P] Add rate limiting middleware for all API endpoints in backend/app/middleware/rate_limiter.py
- [ ] T154 [P] Add input sanitization for all user inputs in backend/app/services/
- [ ] T155 [P] Add CSRF protection in backend/app/main.py
- [ ] T156 [P] Add security headers in backend/app/main.py

### Documentation

- [ ] T157 [P] Add OpenAPI documentation enhancements in backend/app/main.py
- [ ] T158 [P] Create API usage examples in shared/docs/api-examples.md
- [ ] T159 [P] Create deployment guide in shared/docs/deployment.md

### Accessibility

- [ ] T160 [P] Run axe-core accessibility audit on frontend
- [ ] T161 [P] Add ARIA labels to all interactive components in frontend/src/components/
- [ ] T162 [P] Test keyboard navigation across all pages

### Testing Validation

- [ ] T163 Run quickstart.md test scenarios to validate all features
- [ ] T164 Create end-to-end test for full user journey (upload → summarize → Q&A)
- [ ] T165 Verify performance benchmarks meet success criteria

### DevOps

- [ ] T166 [P] Create production Docker configuration in docker/
- [ ] T167 [P] Setup CI/CD pipeline configuration
- [ ] T168 [P] Create database backup scripts in shared/scripts/
- [ ] T169 [P] Create deployment automation scripts in shared/scripts/

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **User Profile (Phase 6)**: Can start after Foundational, but typically after US1-US3
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Uses Document model from US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses Document and DocumentChunk from US1 but independently testable

### Within Each User Story

- Models before services
- Services before endpoints
- Schemas before endpoints
- Core implementations before API endpoints
- Backend before frontend (or in parallel with defined API contract)
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:

- T003, T004, T005, T006, T007, T008 can all run in parallel

**Phase 2 (Foundational - Backend)**:

- T010, T011, T012, T014, T015, T016, T017, T018, T020, T021 can run in parallel after T009
- T030, T031, T032, T033 can run in parallel

**Phase 2 (Foundational - Frontend)**:

- T035, T036, T037, T038, T039, T040, T041 can run in parallel after T034
- T042, T044, T045 can run in parallel

**User Story 1**:

- Models (T046, T047, T048) can run in parallel
- Parsers (T051, T052, T053, T054) can run in parallel
- Storage implementations (T059, T060) can run in parallel
- Frontend types (T069), components (T071, T072, T073, T074) can run in parallel
- API hooks (T077, T078, T079) can run in parallel

**User Story 2**:

- AI providers (T087, T088) can run in parallel
- Frontend components (T095, T096, T097) can run in parallel

**User Story 3**:

- Models (T104, T105) can run in parallel
- Frontend components (T119, T120, T121, T122, T123) can run in parallel

**Phase 6 (User Profile)**:

- Backend endpoints (T133, T134) can run in parallel
- Schemas (T138) can run independently
- Frontend components (T139, T140, T141) can run in parallel

**Phase 7 (Polish)**:

- Most tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all models for User Story 1 together:
Task T046: "Create Document model in backend/app/models/document.py"
Task T047: "Create DocumentChunk model in backend/app/models/document_chunk.py"
Task T048: "Create ReadingHistory model in backend/app/models/reading_history.py"

# Launch all parsers together:
Task T051: "Implement PDF parser using PyMuPDF in backend/app/core/document_parser/pdf_parser.py"
Task T052: "Implement EPUB parser using ebooklib in backend/app/core/document_parser/epub_parser.py"
Task T053: "Implement DOCX parser using python-docx in backend/app/core/document_parser/docx_parser.py"
Task T054: "Implement Markdown parser in backend/app/core/document_parser/markdown_parser.py"

# Launch frontend components together:
Task T071: "Create DocumentUploader component with drag-and-drop in frontend/src/components/document/DocumentUploader.tsx"
Task T072: "Create DocumentList component with status indicators in frontend/src/components/document/DocumentList.tsx"
Task T073: "Create DocumentCard component in frontend/src/components/document/DocumentCard.tsx"
Task T074: "Create ProcessingStatusBadge component in frontend/src/components/document/ProcessingStatusBadge.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T045) **CRITICAL** - blocks all stories
3. Complete Phase 3: User Story 1 (T046-T083)
4. **STOP and VALIDATE**: Test User Story 1 independently using quickstart.md scenarios
5. Deploy/demo if ready

**Estimated Effort**: ~4-6 weeks for MVP (User Story 1)

### Incremental Delivery

1. Complete Setup + Foundational (T001-T045) → Foundation ready
2. Add User Story 1 (T046-T083) → Test independently → Deploy/Demo **(MVP!)**
3. Add User Story 2 (T084-T103) → Test independently → Deploy/Demo
4. Add User Story 3 (T104-T132) → Test independently → Deploy/Demo
5. Add User Profile (T133-T144) → Deploy/Demo
6. Add Polish & Cross-Cutting (T145-T169) → Final Release

**Estimated Total Effort**: ~10-14 weeks for complete feature

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (2-3 weeks)
2. Once Foundational is done:
   - **Developer A**: User Story 1 - Backend (T046-T068)
   - **Developer B**: User Story 1 - Frontend (T069-T083)
   - **Developer C**: Start on User Story 2 - Backend (T084-T094) after US1 models ready
3. Stories complete and integrate independently

With full team (4+ developers):

- Can work on US1, US2, US3 simultaneously after Foundational phase
- Requires clear API contracts and communication

---

## Task Count Summary

- **Phase 1 (Setup)**: 8 tasks
- **Phase 2 (Foundational)**: 37 tasks (13 parallel opportunities)
- **Phase 3 (User Story 1)**: 38 tasks (20 parallel opportunities) 🎯 **MVP**
- **Phase 4 (User Story 2)**: 20 tasks (8 parallel opportunities)
- **Phase 5 (User Story 3)**: 29 tasks (10 parallel opportunities)
- **Phase 6 (User Profile)**: 12 tasks (5 parallel opportunities)
- **Phase 7 (Polish)**: 24 tasks (18 parallel opportunities)

**Total**: 169 tasks

### Breakdown by User Story

- **User Story 1 (Document Upload and Processing)**: 38 tasks
- **User Story 2 (AI-Powered Summarization)**: 20 tasks
- **User Story 3 (Context-Aware Q&A)**: 29 tasks
- **Supporting Infrastructure**: 82 tasks

### Parallel Opportunities Identified

- **Phase 1**: 7 tasks can run in parallel
- **Phase 2**: 13 groups of parallel tasks
- **User Story 1**: 20 tasks can run in parallel
- **User Story 2**: 8 tasks can run in parallel
- **User Story 3**: 10 tasks can run in parallel
- **User Profile**: 5 tasks can run in parallel
- **Polish**: 18 tasks can run in parallel

**Total Parallel Opportunities**: ~81 tasks can be parallelized

---

## Notes

- **[P] tasks**: Different files, no dependencies - can run in parallel
- **[Story] label**: Maps task to specific user story for traceability
- **Each user story**: Independently completable and testable
- **File paths**: All paths are explicit for easy task execution
- **Commit strategy**: Commit after each task or logical group
- **Checkpoints**: Stop at each checkpoint to validate story independently
- **API contracts**: Defined in contracts/openapi.yaml - frontend and backend can work in parallel
- **Testing**: Tests are NOT included as they were not explicitly requested in the specification

---

## Suggested MVP Scope

**Minimum Viable Product** = Phase 1 + Phase 2 + Phase 3 (User Story 1)

This delivers:
✅ User authentication and authorization
✅ Document upload (PDF, EPUB, DOCX, Markdown)
✅ Async document processing (text extraction, chunking, embedding)
✅ Document library with status tracking
✅ Vector database integration for future AI features
✅ Fully functional backend API
✅ Complete frontend UI for document management

**Value Delivered**: Users can upload and manage documents, with full backend infrastructure ready for AI features (summarization and Q&A) in subsequent releases.

**Time to Market**: ~4-6 weeks with 2-3 developers

---

## Format Validation

✅ **All tasks follow the checklist format**: `- [ ] [TaskID] [P?] [Story?] Description with file path`
✅ **Task IDs**: Sequential from T001 to T169
✅ **[P] markers**: Included only for parallelizable tasks (different files, no dependencies)
✅ **[Story] labels**: Included only for user story tasks (US1, US2, US3)
✅ **File paths**: All task descriptions include exact file paths
✅ **Checkpoints**: Clear validation points after each user story
✅ **Independent testing**: Each user story can be tested independently per spec.md

---

**Ready for implementation!** 🚀
