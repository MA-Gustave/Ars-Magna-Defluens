# Ars Magna Defluens — Technical Architecture & Data Flow

This document details the architectural choices enabling the ecosystem to scale to 300 languages natively, without duplicating web instances and without maintaining a fleet of compilation servers.

## 1. Zero Duplication: Multi-Tenant Approach (Wordbench)
Instead of deploying 300 distinct web repositories, the system centralizes the interface:
- **Dynamic Routing**: The frontend uses the language code as a parameter (e.g., /workbench/[langCode]).
- **Targeted Loading**: The interface only loads the data, forms, and GF code specific to the requested language.

## 2. Serverless Compilation (GitOps)
The GF compiler is written in Haskell and is highly CPU-intensive. Instead of maintaining complex custom workers and Redis queues, this project leverages **GitHub Actions**.
- **No Custom Infrastructure**: When a user submits a change via the Wordbench, the app simply commits the code to GitHub via API.
- **CI/CD Pipeline**: GitHub Actions provisions a standard Linux runner, installs the GF binary, and executes the compilation.
- **Artifacts**: The pipeline generates a JSON summary of the compilation (AST, errors, coverage) and updates the central state.

## 3. Identity and Zero-Cost Economy
By offloading the compute completely to GitHub's CI infrastructure, the need for a complex "scan credit" economy is eliminated.
- **Single Sign-On**: GitHub OAuth.
- **Attribution**: Commits are made directly on behalf of the authenticated user, preserving the standard open-source contribution graph.
- **Compute Limits**: We rely on standard GitHub Actions concurrency limits rather than building custom rate-limiting middleware.

## 4. The Observatory (Performant Aggregation)
The global aggregation interface must remain extremely fast.
- The observatory never launches a compilation.
- It merely queries the aggregated JSON metadata updated by the GitHub Actions workflows.
- This guarantees instantaneous loading of the global linguistic map.
