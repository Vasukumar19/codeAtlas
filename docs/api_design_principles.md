# API Design Principles

- RESTful resource-based API under `/api/v1/`
- Consistent response envelope for all endpoints: `status`, `message`, `timestamp`, `request_id`, `data`, `errors`, `metadata`
- Use standard HTTP methods: `GET`, `POST`, `PATCH`, `DELETE`
- JWT bearer authentication for protected routes
- Support future OAuth integration via standard auth endpoints
- Standard pagination, filtering, sorting, and search patterns
- Versioned API pathing for future compatibility
- Long-running operations return job resources and support polling
- Real-time support via Server-Sent Events (SSE) for simple unidirectional progress streams, and WebSockets for complex bidirectional workflows
- All endpoints compatible with FastAPI/OpenAPI automatic generation
- Use descriptive and stable resource names; avoid action verbs in URLs
- Maintain immutability for RIM-related resources through versioned references
- **Correlation IDs**: All requests should accept an `X-Request-ID` header for tracing across APIs, workers, and workflows. Returned in response envelope as `request_id`.
- **Idempotency**: Use the `Idempotency-Key` header for state-mutating requests (e.g., imports, refreshes) to prevent accidental duplicate jobs upon retries.

---

# Rate Limiting

Rate limits are enforced per endpoint group to ensure fair usage and system stability. A `429 Too Many Requests` status is returned when limits are exceeded. Rate limit headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`) are included in responses.

- **AI Queries**: 50 requests per minute per user.
- **Repository Operations (Import/Refresh)**: 10 requests per minute per user.
- **Graph & Explorer APIs**: 300 requests per minute per user.
- **Admin APIs**: 100 requests per minute per admin.

---

# Authentication & Authorization

## JWT Authentication

- Scheme: `Authorization: Bearer <access_token>`
- Access token expiry: short-lived
- Refresh token: returned via secure HTTP-only cookie or via `/auth/refresh`
- Protect all repository, processing, graph, execution, analysis, AI, session, and admin routes
- Public endpoints: health check, auth login, auth refresh

## Authorization Roles

Authorization is handled separately from authentication. The roles are defined as:
- **User**: Standard role for accessing assigned repositories, running AI queries, and interacting with graph data.
- **Admin**: Elevated role with access to system health, queue metrics, caching, embeddings, database status, and global repository management.

## Endpoints

### `POST /api/v1/auth/login`
- Purpose: authenticate user and return access/refresh tokens
- Auth: none
- Request Body:
  - `email` string, required
  - `password` string, required
- Response Schema: `AuthResponse`
- Error Codes: `400`, `401`, `429`
- Example Request:
  ```json
  {
    "email": "alice@example.com",
    "password": "strong-password"
  }
  ```
- Example Response:
  ```json
  {
    "status": "success",
    "message": "Login successful",
    "timestamp": "...",
    "request_id": "...",
    "data": {
      "access_token": "...",
      "refresh_token": "...",
      "expires_in": 3600,
      "user": { "id": "...", "email": "alice@example.com", "name": "Alice", "role": "user" }
    },
    "errors": null,
    "metadata": {}
  }
  ```

### `POST /api/v1/auth/logout`
- Purpose: revoke current refresh token and logout user
- Auth: required
- Request Body: none
- Response Schema: `StandardResponse`
- Error Codes: `401`, `403`

### `POST /api/v1/auth/refresh`
- Purpose: refresh access token using refresh token
- Auth: none, but requires refresh cookie/refresh token
- Request Body:
  - `refresh_token` string, required if not cookie-based
- Response Schema: `AuthResponse`
- Error Codes: `400`, `401`

### `GET /api/v1/auth/me`
- Purpose: retrieve current authenticated user
- Auth: required
- Request Body: none
- Response Schema: `UserResponse`
- Error Codes: `401`

---

# API Groups

1. Repository APIs
2. Repository Processing APIs
3. Graph APIs
4. Repository Explorer APIs
5. Execution APIs
6. Analysis APIs
7. AI APIs
8. Session APIs
9. Administration APIs

---

# Endpoint Definitions

## 1. Repository APIs

### `POST /api/v1/repositories/import`
- Purpose: import a GitHub repository and create a new repository record
- Auth: required
- Headers:
  - `Idempotency-Key` string, recommended for safe retries
- Request Body:
  - `provider` string, required
  - `owner` string, required
  - `name` string, required
  - `default_branch` string, optional
  - `remote_url` string, optional
  - `auth_token` string, optional
- Response Schema: `RepositoryImportResponse`
- Error Codes: `400`, `401`, `409`, `422`

### `POST /api/v1/repositories/{repository_id}/refresh`
- Purpose: refresh an existing repository analysis by creating a new RIM version
- Auth: required
- Headers:
  - `Idempotency-Key` string, recommended
- Path Parameters:
  - `repository_id` UUID
- Request Body:
  - `branch` string, optional
  - `commit_hash` string, optional
- Response Schema: `JobCreatedResponse`
- Error Codes: `400`, `401`, `404`, `409`

### `DELETE /api/v1/repositories/{repository_id}`
- Purpose: delete repository metadata and optionally archives analysis data
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `hard_delete` boolean, optional, default `false`
- Response Schema: `StandardResponse`
- Error Codes: `401`, `403`, `404`

### `GET /api/v1/repositories/{repository_id}`
- Purpose: retrieve repository details
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Response Schema: `RepositoryDetailsResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/status`
- Purpose: retrieve repository import and analysis status
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Response Schema: `RepositoryStatusResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/versions`
- Purpose: list repository analysis versions
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `page`, `per_page`, `sort`, `branch`
- Response Schema: `PaginatedRepositoryVersionResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/metrics`
- Purpose: get persisted repository metrics
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `version` integer, optional
- Response Schema: `RepositoryMetricsResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/languages`
- Purpose: list languages used in the repository
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `version` integer, optional
- Response Schema: `RepositoryLanguagesResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/statistics`
- Purpose: retrieve repository statistics and historical counts
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `version` integer, optional
- Response Schema: `RepositoryStatisticsResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/sessions`
- Purpose: list sessions attached to a repository
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `page`, `per_page`
- Response Schema: `PaginatedSessionResponse`
- Error Codes: `401`, `404`

---

## 2. Repository Processing APIs

### `POST /api/v1/repositories/{repository_id}/analysis/start`
- Purpose: start analysis for the latest repository version
- Auth: required
- Headers:
  - `Idempotency-Key` string, recommended
- Path Parameters:
  - `repository_id` UUID
- Request Body:
  - `version` integer, optional
  - `force` boolean, optional
- Response Schema: `JobCreatedResponse`
- Error Codes: `400`, `401`, `404`

### `POST /api/v1/repositories/{repository_id}/analysis/cancel`
- Purpose: cancel a running analysis job
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Request Body:
  - `job_id` UUID
- Response Schema: `StandardResponse`
- Error Codes: `400`, `401`, `404`, `409`

### `POST /api/v1/repositories/{repository_id}/analysis/retry`
- Purpose: retry failed analysis or restart a completed analysis as new version
- Auth: required
- Headers:
  - `Idempotency-Key` string, recommended
- Path Parameters:
  - `repository_id` UUID
- Request Body:
  - `job_id` UUID optional
  - `version` integer optional
- Response Schema: `JobCreatedResponse`
- Error Codes: `400`, `401`, `404`

### `GET /api/v1/jobs/{job_id}`
- Purpose: retrieve job status and metadata
- Auth: required
- Path Parameters:
  - `job_id` UUID
- Response Schema: `JobStatusResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/jobs/{job_id}/logs`
- Purpose: retrieve logs or event stream for a job
- Auth: required
- Path Parameters:
  - `job_id` UUID
- Query Parameters:
  - `since` timestamp optional
- Response Schema: `JobLogsResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/pipeline/status`
- Purpose: retrieve pipeline stage status for latest or selected version
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `version` integer optional
- Response Schema: `PipelineStatusResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/lifecycle`
- Purpose: retrieve repository lifecycle history and states
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Response Schema: `RepositoryLifecycleResponse`
- Error Codes: `401`, `404`

---

## 3. Graph APIs

### `GET /api/v1/repositories/{repository_id}/graph`
- Purpose: retrieve an aggregated graph overview for the repository version
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `version` integer optional
  - `graph_type` string optional (`call`, `dependency`, `route`, `all`)
  - `page`, `per_page`
- Response Schema: `GraphOverviewResponse`
- Error Codes: `401`, `404`

### `POST /api/v1/repositories/{repository_id}/graph/batch`
- Purpose: fetch multiple nodes and edges in a single request to reduce round-trips
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Request Body:
  - `node_ids` array of UUID optional
  - `edge_ids` array of UUID optional
  - `version` integer optional
- Response Schema: `GraphBatchResponse`
- Error Codes: `400`, `401`, `404`

### `GET /api/v1/repositories/{repository_id}/graph/call`
- Purpose: retrieve call graph data for a repository version
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `version` integer optional
  - `node_id` UUID optional
  - `page`, `per_page`
- Response Schema: `GraphResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/graph/dependency`
- Purpose: retrieve dependency graph data
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Response Schema: `GraphResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/graph/route`
- Purpose: retrieve route graph data
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Response Schema: `GraphResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/graph/nodes/{node_id}`
- Purpose: retrieve details for a single graph node
- Auth: required
- Path Parameters:
  - `repository_id` UUID
  - `node_id` UUID
- Query Parameters:
  - `version` integer optional
- Response Schema: `GraphNodeResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/graph/nodes/{node_id}/neighbors`
- Purpose: retrieve neighboring nodes for a graph node
- Auth: required
- Path Parameters:
  - `repository_id` UUID
  - `node_id` UUID
- Query Parameters:
  - `version` integer optional
  - `direction` string optional (`incoming`, `outgoing`, `both`)
  - `page`, `per_page`
- Response Schema: `GraphNeighborsResponse`
- Error Codes: `401`, `404`

### `POST /api/v1/repositories/{repository_id}/graph/query`
- Purpose: execute a graph search query
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Request Body:
  - `query` string, required
  - `graph_type` string optional
  - `filters` object optional
  - `version` integer optional
- Response Schema: `GraphQueryResponse`
- Error Codes: `400`, `401`, `404`

### `POST /api/v1/repositories/{repository_id}/graph/path`
- Purpose: compute paths between graph nodes
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Request Body:
  - `source_node_id` UUID required
  - `target_node_id` UUID required
  - `graph_type` string optional
  - `max_hops` integer optional
- Response Schema: `GraphPathResponse`
- Error Codes: `400`, `401`, `404`

### `GET /api/v1/repositories/{repository_id}/graph/statistics`
- Purpose: retrieve graph statistics and metrics
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `version` integer optional
- Response Schema: `GraphStatisticsResponse`
- Error Codes: `401`, `404`

---

## 4. Repository Explorer APIs

### `GET /api/v1/repositories/{repository_id}/files`
- Purpose: list repository files
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `version` integer optional
  - `path` string optional
  - `language` string optional
  - `page`, `per_page`, `sort`
- Response Schema: `PaginatedFilesResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/files/{file_id}`
- Purpose: get file metadata and contents
- Auth: required
- Path Parameters:
  - `repository_id` UUID
  - `file_id` UUID
- Query Parameters:
  - `version` integer optional
- Response Schema: `FileResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/symbols`
- Purpose: list symbols in the repository
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `version` integer optional
  - `name` string optional
  - `kind` string optional
  - `scope` string optional
  - `page`, `per_page`
- Response Schema: `PaginatedSymbolsResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/classes`
- Purpose: list classes in the repository
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `version` integer optional
  - `name` string optional
  - `page`, `per_page`
- Response Schema: `PaginatedClassesResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/functions`
- Purpose: list functions in the repository
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `version` integer optional
  - `name` string optional
  - `page`, `per_page`
- Response Schema: `PaginatedFunctionsResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/routes`
- Purpose: list application routes
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `version` integer optional
  - `route_path` string optional
  - `http_method` string optional
  - `page`, `per_page`
- Response Schema: `PaginatedRoutesResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/search`
- Purpose: search repository contents and metadata
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `q` string required
  - `version` integer optional
  - `type` string optional (`file`, `symbol`, `route`, `text`)
  - `page`, `per_page`
- Response Schema: `SearchResponse`
- Error Codes: `400`, `401`, `404`

### `GET /api/v1/repositories/{repository_id}/search/symbols`
- Purpose: search symbols specifically
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `q` string required
  - `version` integer optional
  - `page`, `per_page`
- Response Schema: `SearchResponse`
- Error Codes: `400`, `401`, `404`

### `GET /api/v1/repositories/{repository_id}/search/files`
- Purpose: search files specifically
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `q` string required
  - `version` integer optional
  - `page`, `per_page`
- Response Schema: `SearchResponse`
- Error Codes: `400`, `401`, `404`

---

## 5. Execution APIs

### `POST /api/v1/repositories/{repository_id}/execution-trace`
- Purpose: compute an execution trace from an entry symbol or path
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Request Body:
  - `entry_symbol_id` UUID optional
  - `entry_function_id` UUID optional
  - `path` string optional
  - `version` integer optional
  - `max_depth` integer optional
- Response Schema: `ExecutionTraceResponse`
- Error Codes: `400`, `401`, `404`

### `POST /api/v1/repositories/{repository_id}/execution-flow`
- Purpose: compute high-level execution flow for a feature or route
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Request Body:
  - `route_id` UUID optional
  - `entry_function_id` UUID optional
  - `version` integer optional
- Response Schema: `ExecutionFlowResponse`
- Error Codes: `400`, `401`, `404`

### `POST /api/v1/repositories/{repository_id}/functions/{function_id}/trace`
- Purpose: trace execution of a specific function
- Auth: required
- Path Parameters:
  - `repository_id` UUID
  - `function_id` UUID
- Request Body:
  - `version` integer optional
  - `max_depth` integer optional
- Response Schema: `FunctionTraceResponse`
- Error Codes: `400`, `401`, `404`

### `POST /api/v1/repositories/{repository_id}/functions/{function_id}/call-chain`
- Purpose: retrieve upstream/downstream call chain for a function
- Auth: required
- Path Parameters:
  - `repository_id` UUID
  - `function_id` UUID
- Query Parameters:
  - `direction` string optional (`upstream`, `downstream`, `both`)
  - `max_hops` integer optional
  - `version` integer optional
- Response Schema: `CallChainResponse`
- Error Codes: `400`, `401`, `404`

### `POST /api/v1/repositories/{repository_id}/functions/{function_id}/dependency-chain`
- Purpose: retrieve dependency chain for a function
- Auth: required
- Path Parameters:
  - `repository_id` UUID
  - `function_id` UUID
- Query Parameters:
  - `direction` string optional (`depends_on`, `used_by`)
  - `max_hops` integer optional
  - `version` integer optional
- Response Schema: `DependencyChainResponse`
- Error Codes: `400`, `401`, `404`

---

## 6. Analysis APIs

### `POST /api/v1/repositories/{repository_id}/impact-analysis`
- Purpose: run impact analysis for a change set or function
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Request Body:
  - `affected_symbols` array of UUID
  - `affected_files` array of UUID
  - `version` integer optional
  - `analysis_name` string optional
- Response Schema: `ImpactAnalysisResponse`
- Error Codes: `400`, `401`, `404`

### `POST /api/v1/repositories/{repository_id}/bug-investigation`
- Purpose: perform bug investigation using RIE and repository context
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Request Body:
  - `query` string required
  - `related_files` array of UUID optional
  - `version` integer optional
- Response Schema: `BugInvestigationResponse`
- Error Codes: `400`, `401`, `404`

### `GET /api/v1/repositories/{repository_id}/summary`
- Purpose: retrieve repository summary and high-level RIM overview
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `version` integer optional
- Response Schema: `RepositorySummaryResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/architecture`
- Purpose: retrieve architectural summary and component map
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `version` integer optional
- Response Schema: `ArchitectureSummaryResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/health`
- Purpose: retrieve repository health indicators
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `version` integer optional
- Response Schema: `RepositoryHealthResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/complexity`
- Purpose: retrieve complexity report
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `version` integer optional
- Response Schema: `ComplexityReportResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/heatmap`
- Purpose: retrieve heatmap metrics
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `version` integer optional
  - `metric_name` string optional
- Response Schema: `HeatmapResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/repositories/{repository_id}/dead-code`
- Purpose: retrieve dead code detection report
- Auth: required
- Path Parameters:
  - `repository_id` UUID
- Query Parameters:
  - `version` integer optional
- Response Schema: `DeadCodeReportResponse`
- Error Codes: `401`, `404`

---

## 7. AI APIs

### `POST /api/v1/ai/chat`
- Purpose: conduct chat-style conversation against repository context
- Auth: required
- Request Body:
  - `repository_id` UUID required
  - `session_id` UUID optional
  - `message` string required
  - `version` integer optional
  - `context_options` object optional
- Response Schema: `AIChatResponse`
- Error Codes: `400`, `401`, `404`

### `POST /api/v1/ai/qna`
- Purpose: answer a specific repository question
- Auth: required
- Request Body:
  - `repository_id` UUID required
  - `question` string required
  - `version` integer optional
  - `context_limit` integer optional
- Response Schema: `AIQnAResponse`
- Error Codes: `400`, `401`, `404`

### `POST /api/v1/ai/architecture-explanation`
- Purpose: explain repository architecture in structured form
- Auth: required
- Request Body:
  - `repository_id` UUID required
  - `topic` string optional
  - `version` integer optional
- Response Schema: `AIExplanationResponse`
- Error Codes: `400`, `401`, `404`

### `POST /api/v1/ai/code-explanation`
- Purpose: explain a code snippet, function, or file
- Auth: required
- Request Body:
  - `repository_id` UUID required
  - `file_id` UUID optional
  - `function_id` UUID optional
  - `code_snippet` string optional
  - `version` integer optional
- Response Schema: `AIExplanationResponse`
- Error Codes: `400`, `401`, `404`

### `POST /api/v1/ai/flow-explanation`
- Purpose: explain execution flow or control path
- Auth: required
- Request Body:
  - `repository_id` UUID required
  - `trace_id` UUID optional
  - `route_id` UUID optional
  - `version` integer optional
- Response Schema: `AIExplanationResponse`
- Error Codes: `400`, `401`, `404`

### `POST /api/v1/ai/context-retrieval`
- Purpose: retrieve relevant repository context for a query
- Auth: required
- Request Body:
  - `repository_id` UUID required
  - `query` string required
  - `version` integer optional
  - `top_k` integer optional
- Response Schema: `ContextRetrievalResponse`
- Error Codes: `400`, `401`, `404`

### `POST /api/v1/ai/tool-execution`
- Purpose: execute a registered RIE tool and get structured results
- Auth: required
- Request Body:
  - `repository_id` UUID required
  - `tool_name` string required
  - `tool_version` string optional
  - `input` object required
  - `version` integer optional
- Response Schema: `ToolExecutionResponse`
- Error Codes: `400`, `401`, `404`

### `GET /api/v1/ai/conversations/{conversation_id}`
- Purpose: retrieve a conversation record
- Auth: required
- Path Parameters:
  - `conversation_id` UUID
- Response Schema: `ConversationResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/ai/conversations/{conversation_id}/history`
- Purpose: retrieve conversation history
- Auth: required
- Path Parameters:
  - `conversation_id` UUID
- Query Parameters:
  - `page`, `per_page`
- Response Schema: `PaginatedConversationHistoryResponse`
- Error Codes: `401`, `404`

---

## 8. Session APIs

### `POST /api/v1/sessions`
- Purpose: create a new repository session
- Auth: required
- Request Body:
  - `repository_id` UUID required
  - `name` string optional
  - `repository_version_id` UUID optional
  - `pinned_files` array optional
  - `graph_viewport` object optional
  - `expanded_nodes` array optional
  - `recent_queries` array optional
  - `conversation_history` array optional
  - `filters` object optional
  - `selected_branch` string optional
  - `selected_version` integer optional
- Response Schema: `RepositorySessionResponse`
- Error Codes: `400`, `401`, `404`

### `PATCH /api/v1/sessions/{session_id}`
- Purpose: update an existing session
- Auth: required
- Path Parameters:
  - `session_id` UUID
- Request Body:
  - any session fields as partial update
- Response Schema: `RepositorySessionResponse`
- Error Codes: `400`, `401`, `404`

### `DELETE /api/v1/sessions/{session_id}`
- Purpose: delete a session
- Auth: required
- Path Parameters:
  - `session_id` UUID
- Response Schema: `StandardResponse`
- Error Codes: `401`, `404`

### `POST /api/v1/sessions/{session_id}/restore`
- Purpose: restore a session into the UI state
- Auth: required
- Path Parameters:
  - `session_id` UUID
- Response Schema: `RepositorySessionResponse`
- Error Codes: `401`, `404`

### `GET /api/v1/sessions/{session_id}/pinned-files`
- Purpose: retrieve pinned files for a session
- Auth: required
- Path Parameters:
  - `session_id` UUID
- Response Schema: `PinnedFilesResponse`
- Error Codes: `401`, `404`

### `PATCH /api/v1/sessions/{session_id}/graph-state`
- Purpose: update the graph viewport and expand state
- Auth: required
- Path Parameters:
  - `session_id` UUID
- Request Body:
  - `graph_viewport` object optional
  - `expanded_nodes` array optional
- Response Schema: `RepositorySessionResponse`
- Error Codes: `400`, `401`, `404`

### `PATCH /api/v1/sessions/{session_id}/workspace-layout`
- Purpose: update workspace layout metadata
- Auth: required
- Path Parameters:
  - `session_id` UUID
- Request Body:
  - `workspace_layout` object required
- Response Schema: `RepositorySessionResponse`
- Error Codes: `400`, `401`, `404`

---

## 9. Administration APIs

### `GET /api/v1/admin/health`
- Purpose: service health check
- Auth: optional for internal admin
- Response Schema: `HealthResponse`
- Error Codes: `503`

### `GET /api/v1/admin/metrics`
- Purpose: system metrics and performance counters
- Auth: required admin
- Response Schema: `SystemMetricsResponse`
- Error Codes: `401`, `403`

### `GET /api/v1/admin/workers`
- Purpose: worker status and health
- Auth: required admin
- Response Schema: `WorkerStatusResponse`
- Error Codes: `401`, `403`

### `GET /api/v1/admin/queue`
- Purpose: job queue metrics and backlog
- Auth: required admin
- Response Schema: `QueueStatusResponse`
- Error Codes: `401`, `403`

### `GET /api/v1/admin/cache`
- Purpose: cache status and hit/miss rates
- Auth: required admin
- Response Schema: `CacheStatusResponse`
- Error Codes: `401`, `403`

### `GET /api/v1/admin/embeddings`
- Purpose: embedding index health and usage
- Auth: required admin
- Response Schema: `EmbeddingStatusResponse`
- Error Codes: `401`, `403`

### `GET /api/v1/admin/database`
- Purpose: database connectivity and health
- Auth: required admin
- Response Schema: `DatabaseStatusResponse`
- Error Codes: `401`, `403`

---

# Request Schemas

## Generic Request Schemas

### `PaginationParams`
- `page` integer, default `1`
- `per_page` integer, default `25`
- `sort` string, optional
- `direction` string, optional, enum `asc`, `desc`

### `SearchParams`
- `q` string required
- `page` integer
- `per_page` integer
- `sort` string
- `scope` string optional

### `JobControlRequest`
- `job_id` UUID required

### `AnalysisStartRequest`
- `version` integer optional
- `force` boolean optional

### `GraphQueryRequest`
- `query` string required
- `graph_type` string optional
- `filters` object optional
- `version` integer optional

### `GraphPathRequest`
- `source_node_id` UUID required
- `target_node_id` UUID required
- `graph_type` string optional
- `max_hops` integer optional

### `ExecutionTraceRequest`
- `entry_symbol_id` UUID optional
- `entry_function_id` UUID optional
- `path` string optional
- `version` integer optional
- `max_depth` integer optional

### `ImpactAnalysisRequest`
- `affected_symbols` array of UUID optional
- `affected_files` array of UUID optional
- `version` integer optional
- `analysis_name` string optional

### `BugInvestigationRequest`
- `query` string required
- `related_files` array of UUID optional
- `version` integer optional

### `AIChatRequest`
- `repository_id` UUID required
- `session_id` UUID optional
- `message` string required
- `version` integer optional
- `context_options` object optional

### `AIToolExecutionRequest`
- `repository_id` UUID required
- `tool_name` string required
- `tool_version` string optional
- `input` object required
- `version` integer optional

### `SessionCreateRequest`
- `repository_id` UUID required
- `name` string optional
- `repository_version_id` UUID optional
- `pinned_files` array optional
- `graph_viewport` object optional
- `expanded_nodes` array optional
- `recent_queries` array optional
- `conversation_history` array optional
- `filters` object optional
- `selected_branch` string optional
- `selected_version` integer optional

---

# Response Schemas

## Standard Response Envelope

### `StandardResponse`
- `status` string enum `success`, `error`
- `message` string
- `timestamp` string (ISO 8601)
- `request_id` string
- `data` object or null
- `errors` array or null
- `metadata` object

## Common Response Models

### `ApiResponse<T>`
- `status`
- `message`
- `timestamp`
- `request_id`
- `data` T
- `errors`
- `metadata`

### `PaginatedResponse<T>`
- `status`
- `message`
- `timestamp`
- `request_id`
- `data`
  - `items` array of T
  - `page`
  - `per_page`
  - `total_items`
  - `total_pages`
- `errors`
- `metadata`

## Example Specific Responses

### `RepositoryDetailsResponse`
- `id`, `provider`, `owner`, `name`, `default_branch`, `remote_url`, `created_at`, `updated_at`, `latest_version`, `status`

### `RepositoryStatusResponse`
- `repository_id`, `version`, `rim_version`, `status`, `current_stage`, `stage_history`

### `JobCreatedResponse`
- `job_id`, `repository_id`, `repository_version_id`, `job_type`, `status`, `queued_at`

### `GraphResponse`
- `nodes`, `edges`, `graph_type`, `version`

### `GraphBatchResponse`
- `nodes`, `edges` (lists matching requested ids)

### `FileResponse`
- `id`, `path`, `language`, `size_bytes`, `file_hash`, `content_preview`, `parsed_at`, `status`

### `ExecutionTraceResponse`
- `trace_id`, `trace_name`, `entry_function_id`, `steps`, `citations`, `metadata`

### `AIChatResponse`
- `conversation_id`, `message_id`, `response`, `structured_response`, `citations`, `metadata`

### `RepositorySessionResponse`
- `id`, `user_id`, `repository_id`, `repository_version_id`, `name`, `pinned_files`, `graph_viewport`, `expanded_nodes`, `recent_queries`, `conversation_history`, `filters`, `selected_branch`, `selected_version`, `created_at`, `updated_at`

---

# Error Responses

## Standard Error Format

```json
{
  "status": "error",
  "message": "Validation failed",
  "timestamp": "2026-07-10T12:00:00Z",
  "request_id": "uuid",
  "data": null,
  "errors": [
    {
      "code": "INVALID_INPUT",
      "field": "path",
      "message": "Path is required"
    }
  ],
  "metadata": {}
}
```

## Common Error Codes

- `400` Bad Request
  - invalid JSON
  - missing required fields
  - invalid parameter values
- `401` Unauthorized
  - missing or invalid JWT
  - expired access token
- `403` Forbidden
  - insufficient permissions
  - admin-only endpoint
- `404` Not Found
  - repository, job, session, or node not found
- `409` Conflict
  - duplicate repository import
  - concurrent update conflict
- `422` Unprocessable Entity
  - semantic validation failed
  - request shape valid, content invalid
- `429` Too Many Requests
  - rate limit exceeded
- `500` Internal Server Error
  - unexpected processing error
- `503` Service Unavailable
  - downstream service unavailable
  - FAISS or DB outage

---

# Pagination Strategy

- Use query parameters:
  - `page` integer, default `1`
  - `per_page` integer, default `25`, max `100`
  - `sort` string, e.g. `created_at`, `name`
  - `direction` string, `asc` or `desc`
- Response metadata:
  - `page`
  - `per_page`
  - `total_items`
  - `total_pages`
  - `next_page`
  - `prev_page`
- For very large lists, support cursor-based pagination later via:
  - `cursor` string
  - `limit` integer
- Use standard list responses for files, symbols, versions, sessions, workflows, jobs, graph nodes, conversation history

---

# Real-time APIs (WebSockets & SSE)

## Server-Sent Events (SSE)
SSE is the preferred protocol for simple unidirectional progress streams.
Clients can connect via standard HTTP and receive real-time updates.

### `/api/v1/stream/imports/{repository_id}`
- Purpose: stream repository import progress
- Auth: required via JWT query parameter or header

### `/api/v1/stream/analysis/{job_id}`
- Purpose: stream analysis pipeline progress for a job
- Auth: required

### `/api/v1/stream/jobs/{job_id}`
- Purpose: real-time job status events
- Auth: required

## WebSocket Endpoints
WebSockets are reserved for complex, bidirectional communication.

### `/ws/workflows/{workflow_run_id}`
- Purpose: stream workflow execution updates and receive client inputs
- Auth: required
- Messages:
  - `workflow_started`
  - `step_started`
  - `prompt_executed`
  - `tool_executed`
  - `workflow_completed`
  - `workflow_failed`

### `/ws/execution/{trace_id}`
- Purpose: stream execution trace generation progress
- Auth: required

## Message Envelope

```json
{
  "type": "status_update",
  "timestamp": "...",
  "request_id": "...",
  "data": { "stage": "PARSING", "status": "RUNNING" },
  "metadata": {}
}
```

---

# Long Running Job Pattern

### Pattern
1. Client submits `POST` to start a long-running operation
2. Server responds with `job_id`
3. Client polls `GET /api/v1/jobs/{job_id}` or subscribes to SSE stream
4. When job completes, client fetches result from job details or related resource

### Example
- `POST /api/v1/repositories/{repository_id}/analysis/start`
- Response:
  - `job_id`
  - `status`: `QUEUED`
  - `queued_at`
- Poll:
  - `GET /api/v1/jobs/{job_id}`
- Final state:
  - `status`: `SUCCEEDED` or `FAILED`
  - `result`: job outcome metadata

---

# API Versioning & Deprecation

- Base path: `/api/v1/`
- All endpoints defined under versioned path
- Future versions:
  - `/api/v2/`
- Use version path rather than content negotiation
- Keep backward compatible contracts in the same API version

## Deprecation Policy
- Deprecated endpoints will include a `Warning` HTTP header.
- Deprecated API versions (e.g., `/api/v1/` after `/api/v2/` release) will be supported for exactly 12 months after the new version is released.
- Deprecation schedules will be clearly communicated in API documentation and response metadata.

---

# OpenAPI Notes

- Use FastAPI auto-generated OpenAPI models
- Define request/response schemas with Pydantic-compatible structures
- Include examples for key payloads
- Add tags per group:
  - `Repository`
  - `Processing`
  - `Graph`
  - `Explorer`
  - `Execution`
  - `Analysis`
  - `AI`
  - `Session`
  - `Admin`
  - `Auth`
- Document authentication via `Bearer` auth scheme
- Use response models for success and error types
- Mark required fields explicitly
- Use `description` and `summary` metadata for each endpoint
- Ensure JSON request bodies are validated with schema definitions
- Support OpenAPI auto docs at docs and `/redoc`
