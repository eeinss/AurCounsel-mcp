# Architecture

This document intentionally describes only the public architectural boundary of AurCounsel MCP.

## Public architecture

```text
MCP Client
    ↓
AurCounsel MCP
    ↓
AurCounsel Contract Intelligence Engine
    ├── Contract Review
    ├── Drafting
    ├── Comparison
    ├── Legal Grounding
    └── Artifact Generation
```

## MCP Client

Any compatible client can use the public MCP interface according to the live transport and tool schemas. Client responsibilities include:

- discovering available tools;
- submitting valid tool inputs;
- preserving returned job identifiers;
- observing job state;
- retrieving completed artifacts;
- handling failures without misrepresenting terminal state.

## AurCounsel MCP

AurCounsel MCP is the public protocol boundary. It exposes developer-facing capabilities while isolating internal implementation details.

Its public responsibilities include:

- exposing the supported tool contract;
- accepting contract intelligence requests;
- returning job identifiers for asynchronous work;
- reporting public job state;
- delivering completed artifacts through the public artifact interface.

## AurCounsel Contract Intelligence Engine

The engine behind the MCP boundary provides product capabilities including:

- **Contract Review** — review contract content and produce review deliverables.
- **Drafting** — generate contract drafting deliverables from accepted input.
- **Comparison** — analyze contracts or versions and produce comparison deliverables.
- **Legal Grounding** — ground supported contract intelligence workflows in applicable legal knowledge.
- **Artifact Generation** — package successful outputs into retrievable public deliverables.

This high-level description is a product capability map, not a disclosure of internal pipeline stages.

## Deliberately out of scope

This repository must not document or expose:

- production launchers or internal filesystem paths;
- production database structure or snapshots;
- internal message buses, reviewer/executor records, or release-validation traces;
- private contracts, uploaded fixtures, or production user data;
- credentials or secrets;
- tunnel or edge-network configuration;
- internal model endpoints or host addresses;
- private prompts;
- Legal Knowledge Release source data;
- private signal implementations;
- internal gate source code;
- private legal corpus;
- detailed production topology.

## Trust boundary

Developers should treat the MCP tool schemas, job status contract, error semantics, and artifact contract as the supported public boundary. Everything behind that boundary is implementation detail unless explicitly documented as public.
