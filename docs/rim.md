# RIM Principles

The Repository Intelligence Model (RIM) is the single source of truth for CodeAtlas. It is the canonical internal representation of every analyzed repository, consumed by the Parser, Graph Engine, Repository Intelligence Engine (RIE), Retrieval Engine, API Layer, and Frontend. No service may invent its own internal representation.

- **Immutable**: Once a RIM object is created and committed for a version, it cannot be modified.
- **Versioned**: All objects are tied to a specific `repository_version_id`.
- **Language Agnostic**: Capable of representing any programming language uniformly.
- **Serializable**: Every object serializes deterministically to canonical JSON.
- **Extensible**: Designed to support future language features, graph types, and AI tools without breaking changes.
- **Strongly Typed**: Schema-enforced fields and relationships.
- **Stable IDs**: Deterministic ID generation to ensure object identities are stable across versions if the underlying entity hasn't changed.
- **Backward Compatible**: Additive changes only; no removal or breaking schema modifications.

# Object Hierarchy

The RIM hierarchy flows from the root repository down to specific tokens and AI reasoning steps.

- **Base**: Entity -> Location
- **Core**: Repository -> Repository Version -> Directory -> Repository File / Module / Package / Namespace -> Language
- **Parser**: AST -> AST Node -> Token | Comment | Annotation | Decorator | Import | Export | Route | Symbol -> ExecutableSymbol | StructuralSymbol | DataSymbol
- **Graph**: Graph -> Graph Node | Graph Edge
- **Analysis**: Execution Trace -> Execution Step | Call Chain | Dependency Chain | Impact Analysis | Bug Investigation | Complexity Metrics | Heatmap | Architecture Summary
- **Embedding**: Embedding Chunk -> Chunk Metadata | Chunk Source | Chunk References
- **AI**: Intent -> Query Plan -> Context Window -> Retrieved Context -> Reasoning Step -> Tool Call -> Response -> Citation

# Object Definitions

Each object definition below follows the standard RIM layout.
- **Versioning Rules**: All objects are immutable. Re-parsing creates a new object instance linked to a new `repository_version_id`. If the content/hash is unchanged, the same Unique ID is retained in the new version.
- **Serialization Format**: Canonical JSON (schema validated).
- **Unique ID Strategy**: Deterministically generated UUIDv5 based on parent ID and intrinsic properties (e.g., file path, symbol signature, AST node location).

## Base Objects

### Entity
- **Purpose**: The foundational base class for all RIM objects, providing consistent identity and versioning.
- **Fields**: `id`, `repository_id`, `repository_version_id`, `created_at`, `updated_at`, `metadata`.

### Location
- **Purpose**: Canonical representation of a physical location in a source file.
- **Fields**: Inherits Entity + `file_id`, `start_line`, `start_column`, `end_line`, `end_column`.
- **Relationships**: Referenced by AST nodes, symbols, imports, routes, citations, and embeddings.

## Core Objects

### Repository
- **Purpose**: Root identity of a codebase.
- **Fields**: Inherits Entity + `provider`, `owner`, `name`, `remote_url`.
- **Relationships**: 1:M with Repository Version.
- **Parent Object**: None. **Child Objects**: Repository Version.

### Repository Version
- **Purpose**: A snapshot of the repository at a specific commit.
- **Fields**: Inherits Entity + `commit_hash`, `branch_name`.
- **Relationships**: 1:M with all Version-scoped objects.
- **Parent Object**: Repository. **Child Objects**: Directory, Repository File, Graph, Execution Trace.
- **Unique ID Strategy**: UUIDv5(Repository ID + Commit Hash).

### Repository File
- **Purpose**: Represents a source file in the repository.
- **Fields**: Inherits Entity + `path`, `language_id`, `file_hash`, `size_bytes`.
- **Relationships**: 1:1 with AST, 1:M with Symbol.
- **Parent Object**: Directory. **Child Objects**: AST, Symbol, Module.
- **Unique ID Strategy**: UUIDv5(Repository Version ID + File Path).

### Language
- **Purpose**: Defines language semantics and parser configuration.
- **Fields**: Inherits Entity + `name`, `extensions`, `parser_version`.
- **Parent Object**: None. **Child Objects**: None.

### Directory
- **Purpose**: Represents the filesystem structure.
- **Fields**: Inherits Entity + `path`.
- **Parent Object**: Directory. **Child Objects**: Directory, Repository File.

### Module / Package / Namespace
- **Purpose**: Represents logical groupings of code.
- **Fields**: Inherits Entity + `name`, `fully_qualified_name`.
- **Parent Object**: Repository Version. **Child Objects**: Symbol.

## Parser Objects

*(All parser objects inherit from Entity. UUIDv5 is generated from File ID + Location or signature).*

### AST & AST Node & AST Edge
- **Purpose**: Syntactic representation of a file.
- **Fields**: Inherits Entity + `location_id`, `type`, `code_snippet`.
- **Relationships**: AST 1:M Node, Node 1:M Edge (Child/Sibling).
- **Child Objects**: Token, Comment.

### Token / Comment / Annotation / Decorator
- **Purpose**: Finer-grained syntactic metadata.
- **Fields**: Inherits Entity + `ast_node_id`, `location_id`, `content`.

### Import / Export / Route
- **Purpose**: Dependency and API boundaries.
- **Fields**: Inherits Entity + `location_id`, `source`, `target`, `alias`, `http_method`, `route_path`.

### Symbol (Base)
- **Purpose**: Identifiable semantic construct.
- **Fields**: Inherits Entity + `name`, `fully_qualified_name`, `visibility`, `ast_node_id`, `location_id`.
- **Relationships**: 1:M with Symbol Graph Nodes.

### ExecutableSymbol (Function / Method)
- **Purpose**: Concrete executable symbols. Traces and dynamic analysis operate exclusively on these.
- **Fields**: Inherits Symbol + `signature`, `return_type`, `parameters`, `is_async`.

### StructuralSymbol (Class / Interface / Struct / Trait)
- **Purpose**: Structural type definitions and object blueprints.
- **Fields**: Inherits Symbol + `inheritance_ids`, `implementation_ids`.

### DataSymbol (Variable / Constant / Enum / Type Alias)
- **Purpose**: Data definitions and constraints.
- **Fields**: Inherits Symbol + `type_annotation`, `value`, `is_mutable`.

## Graph Objects

### Graph
- **Purpose**: Container for a specific topological model.
- **Fields**: Inherits Entity + `graph_type` (Enum: `CALL`, `DEPENDENCY`, `IMPORT`, `ROUTE`, `SYMBOL`, `CFG`, `DATAFLOW`), `node_count`, `edge_count`.
- **Unique ID Strategy**: UUIDv5(Graph Type + Repository Version ID).

### Graph Node
- **Purpose**: Vertex in the graph, resolving back to a core RIM object.
- **Fields**: Inherits Entity + `graph_id`, `entity_id` (e.g. Symbol ID, File ID).

### Graph Edge
- **Purpose**: Directed relationship between two nodes.
- **Fields**: Inherits Entity + `graph_id`, `source_node_id`, `target_node_id`, `weight`.

## Analysis Objects

### Execution Trace & Execution Step
- **Purpose**: Represents an analyzed control flow path.
- **Fields**: Inherits Entity + `entry_point_id`, `max_depth` / `trace_id`, `sequence_number`, `executable_symbol_id`, `context`.
- **Parent Object**: Repository Version. **Child Objects**: Execution Step.

### Call Chain / Dependency Chain
- **Purpose**: Upstream/downstream impacts.
- **Fields**: Inherits Entity + `target_symbol_id`, `direction`, `chain_nodes`.

### Impact Analysis / Bug Investigation / Complexity Metrics / Heatmap / Architecture Summary
- **Purpose**: High-level intelligence outputs.
- **Fields**: Inherits Entity + `focus_nodes`, `results_json`, `score`, `metric_type`.

## Embedding Objects

### Embedding Chunk / Chunk Metadata / Chunk Source / Chunk References
- **Purpose**: Vector database representation.
- **Fields**: Inherits Entity + `vector`, `text`, `source_id` (file/symbol), `location_id`.

## AI Objects

*(All AI Objects inherit from Entity and include base AI fields: `confidence`, `retrieval_sources`, `reasoning_trace`, `generated_at`)*

### Intent / Query Plan / Context Window / Retrieved Context / Reasoning Step / Tool Call / Response / Citation
- **Purpose**: Orchestration and state of the RIE.
- **Fields**: Inherits Entity + AI Base Fields + `session_id`, `type`, `prompt`, `parameters`, `result`.
- **Relationships**: Response 1:M Citation (points back to Repository File or Location).

# Relationships

- **One-to-One**: File -> AST, Symbol -> Graph Node.
- **One-to-Many**: Version -> File, File -> Symbol, Graph -> Edge.
- **Many-to-Many**: Files <-> Dependencies (via Import Graph), Symbols <-> Symbols (via Call Graph).
- **Cross References**: Annotations -> Routes, Comments -> Symbols.
- **Graph References**: Graph Node -> Entity (Symbol/File).
- **AST References**: Symbol -> AST Node (for exact location and code).
- **Embedding References**: Chunk -> AST Node / Symbol / Location (for source attribution).

# Identity Rules

- **Universal Identifiers**: Every object derives from `Entity`, thus possessing `id` (UUID), `repository_id` (UUID), `repository_version_id` (UUID), `created_at`, `updated_at`.
- **No Duplication**: UUIDv5 deterministic generation ensures identical entities in the same version resolve to the same ID, preventing duplicate insertion.

# Versioning

Repository ↓ Repository Version ↓ RIM Version ↓ Graph Version ↓ Embedding Version ↓ Analysis Version

**Stability Rule**: Object references remain stable across versions by decoupling the intrinsic entity identity from the version hash. An AST Node's UUIDv5 is derived from its normalized signature and path, not just its commit hash. Thus, if a function is unchanged between commits A and B, it retains the exact same `id` in the Symbol table across both Repository Versions, allowing historical metrics and graphs to overlay perfectly.

# Serialization

All RIM objects serialize to a canonical JSON schema.

### Example: ExecutableSymbol (Function)
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "repository_id": "...",
  "repository_version_id": "...",
  "created_at": "2026-07-10T12:00:00Z",
  "updated_at": "2026-07-10T12:00:00Z",
  "metadata": {},
  "type": "ExecutableSymbol",
  "name": "calculateTotal",
  "fully_qualified_name": "src.billing.calculateTotal",
  "visibility": "public",
  "ast_node_id": "...",
  "location_id": "...",
  "signature": "calculateTotal(items: List[Item]) -> float",
  "return_type": "float",
  "parameters": ["items: List[Item]"],
  "is_async": false
}
```

# Explicit Provenance

Every generated object maintains an exact traceability path back to its absolute origin. This explicit provenance is required for complete explainability of AI outputs and analysis.

**Example Trace**:
Execution Trace -> Graph IDs -> AST IDs -> File IDs -> Embedding IDs

When answering "Where did this come from?", the RIE traverses these relationships to produce precise `Citation` objects, mapping high-level insights directly to the `Location` in source files.

# Retrieval Model

Retrieval combines multiple vectors into one unified retrieved context:
1. **Metadata**: Hard filters (e.g., language="python", path="src/").
2. **Graph**: Neighbor expansion (e.g., fetch dependencies of the matched node).
3. **AST**: Structural context (e.g., fetch parent class if a method is matched).
4. **Keyword**: BM25 lexical match.
5. **Semantic**: Dense vector similarity (Embeddings).
These feed into a cross-encoder or reciprocal rank fusion (RRF) algorithm to produce a single `Retrieved Context` object.

# Repository Intelligence Engine Integration

RIE consumes RIM entirely natively:
**Intent** (User asks a question)
↓
**Planner** (Generates Query Plan using RIM schemas)
↓
**Retriever** (Executes plan to build Retrieved Context from RIM Embeddings/Graphs)
↓
**Context Builder** (Constructs Context Window mapping RIM objects to prompt tokens)
↓
**Reasoner** (Executes Reasoning Steps)
↓
**Response Formatter** (Yields Response with Citations mapping directly to RIM `Location` or `Symbol`).

# Execution Trace Model

**ExecutableSymbol** (User selects an entry function/method)
↓
**Graph (CALL type)** (Graph Engine traverses out-edges from entry symbol)
↓
**Execution Trace** (Analysis Engine builds sequential Execution Steps)
↓
**AI Explanation** (RIE consumes Execution Trace objects to generate natural language flow descriptions).

# Impact Analysis Model

**Graph Traversal** (Start at changed Symbol/AST Nodes)
↓
**Affected Nodes** (Compute transitive closure via Dependency/Call Graphs)
↓
**Reasoner** (AI evaluates severity of changes on Affected Nodes)
↓
**Response** (Yields Impact Analysis object).

# Extension Points

- **New Languages**: Implement a new Language definition and map its AST to standard RIM Symbol/AST Nodes.
- **New Graph Types**: Introduce a new Enum value for `graph_type` on the base `Graph` object; no schema migrations required.
- **New AI Tools**: Tool Call objects accept arbitrary `parameters` JSON, allowing dynamic registration of tools that operate on RIM IDs.
- **New Metrics/Analysis Types**: Extend the Analysis Object base class; bind `results_json` to domain-specific schemas without altering core RIM structure.
