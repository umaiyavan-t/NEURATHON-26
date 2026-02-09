# KARMIC MVP Implementation Tasks

## Overview

KARMIC is an India‑first freelance platform MVP focused on solving unfair pricing, bidding chaos, lack of contracts, payment insecurity, and missing trust mechanisms in the Indian freelance ecosystem.  
This task list is optimized for fast hackathon development and a smooth live demo.

**MVP success criteria:**

- Job can be posted by a client
- Freelancers are AI‑matched automatically
- Contract is generated and accepted
- Mock escrow payment is released
- Trust score is updated

## Frontend (HTML/CSS/JS)

- [ ] Base layout & navigation: Landing page plus simple navigation between Client and Freelancer views.
- [ ] Client flows UI: Forms for posting jobs, reviewing matched freelancers, viewing proposals, and selecting a freelancer.
- [ ] Freelancer flows UI: Forms for profile creation/edit, adding skills, minimum rate, and language; views for matched jobs and proposal submission.
- [ ] Contract & escrow views: Screens or modals to review contract terms, show escrow state (Pending / In Escrow / Released), and mark job completion.
- [ ] Trust & status indicators: Visual indicators for freelancer trust score and job state on relevant screens.
- [ ] API integration: JavaScript helpers for calling backend APIs (auth, profiles, jobs, matching, contracts, escrow, trust updates) and handling responses/errors.

## Backend (FastAPI APIs)

- [ ] Project setup: FastAPI app skeleton, routing structure, environment configuration, and Supabase client setup.
- [ ] Auth integration: Middleware or utilities to validate Supabase auth tokens on protected endpoints.
- [ ] User & role management: Models and endpoints for Client and Freelancer profiles, including skills, minimum rate, language, and trust score.
- [ ] Job posting APIs: Endpoints to create, list, and fetch jobs with skills, budget, and timeline; scoped to authenticated clients.
- [ ] Proposal APIs: Endpoints for freelancers to submit proposals and for clients to review/list proposals for a job.

## AI Matching & Pricing Guardrails

- [ ] Define rule-based matching criteria: Skill match, rate compatibility, language preference, and (optionally) trust score weighting.
- [ ] Matching endpoint: Endpoint that returns the top 5 freelancers for a given job, ordered by rule-based score.
- [ ] Pricing guardrails: API-level checks that prevent proposals below a freelancer’s minimum rate and enforce fair pricing.
- [ ] Test cases: Unit or integration tests covering no-match scenarios, ties, edge-case pricing, and invalid input.

## Digital Contracts & Mock Escrow

- [ ] Contract model & schema: Data structures for scope, timeline, payment terms, dispute clause, and acceptance states for client and freelancer.
- [ ] Contract lifecycle endpoints: Generate a contract after freelancer selection, fetch contract details, and allow both parties to accept.
- [ ] Escrow state machine: Represent payment states (Pending, In Escrow, Released) with timestamps and basic validation.
- [ ] Mock UPI success flow: Simulated funding into escrow and release on job completion, including status updates visible in the UI.

## Trust Score System

- [ ] Default trust score: Assign an initial trust score to new freelancers when their profile is created.
- [ ] Update logic: Increase trust score after successful job completion; consider simple rules (e.g., fixed increment per completed job).
- [ ] Matching integration: Incorporate trust score as a factor when ordering the top 5 freelancer matches.
- [ ] UI display: Show trust score on freelancer profiles and in client-facing freelancer lists.

## Supabase (Auth & Database)

- [ ] Supabase project setup: Create project (free tier), configure environment variables, and connect FastAPI to Supabase.
- [ ] Schema design: Tables for users, jobs, proposals, contracts, payments/escrow, and trust history.
- [ ] Basic RLS/security: Ensure users can only access their own sensitive records (e.g., proposals, contracts, payments).
- [ ] Seed/demo data: Insert sample freelancers, clients, jobs, and contracts to support demo scenarios.

## Non-Functional Requirements & Demo Prep

- [ ] Performance sanity checks: Verify key endpoints respond quickly on localhost for the main flows.
- [ ] Happy-path demo script: Write a step-by-step scenario from client job posting through matching, contract acceptance, escrow release, and trust score update.
- [ ] Error handling & UX: Add user-friendly messages and fallbacks for common failures (network errors, invalid input, auth issues).
- [ ] Local run instructions: Document how to run the frontend and backend locally, including environment variables and Supabase setup steps.

