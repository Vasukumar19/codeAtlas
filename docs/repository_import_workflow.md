# Repository Import Workflow Decision

## Status

Approved for the Repository Import milestone.

## Decision

Repository Import must be cache-aware and job-based. A GitHub URL must not be
cloned immediately or treated as a new repository by default.

```text
GitHub URL
  ↓
Validate
  ↓
Repository Cache Check
  ↓
Already Indexed?
  ├─ Yes → Return Existing Repository
  └─ No
       ↓
    Create Repository
       ↓
    Create Analysis Job
       ↓
    Clone
       ↓
    Store Snapshot
       ↓
    Repository Ready
```

## Required Behavior

- Validate the GitHub URL before creating persistent records or scheduling work.
- Identify an existing indexed repository using its canonical provider, owner, and
  repository name.
- Return the existing repository when it is already indexed; do not clone or
  analyze it again.
- Create a repository record and an asynchronous analysis job only for a cache
  miss.
- Persist the cloned repository snapshot before marking the repository ready.
- Make repository readiness observable through the analysis job and repository
  status lifecycle.

## Rationale

This workflow prevents duplicate cloning and analysis, conserves processing
capacity, and establishes a stable repository/version lifecycle for later
milestones.
