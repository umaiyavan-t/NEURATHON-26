# WORKLANCE MVP Implementation Tasks

## Overview
Implement WORKLANCE MVP with FastAPI backend, HTML/CSS/JS frontend, Supabase auth/DB. Focus on fast, simple, easy config.

## Frontend (HTML/CSS/JS)
- [x] Base layout & navigation: index.html with sections for login, client, freelancer.
- [x] style.css: Simple styling for UI.
- [x] script.js: API integration, UI logic for login, post job, profile, etc.
- [x] Client flows: Post job form, view jobs, select freelancer.
- [x] Freelancer flows: Edit profile, view matched jobs, submit proposals.
- [ ] Contract & escrow views: Display contract, escrow status.
- [ ] Trust score display.

## Backend (FastAPI APIs)
- [x] Project setup: main.py with FastAPI, CORS, Supabase client.
- [x] Auth integration: Login endpoint (mock for now).
- [x] User & role management: Create/get user profiles.
- [x] Job posting APIs: Post/get jobs.
- [x] Proposal APIs: Submit/get proposals with pricing guardrails.
- [x] AI Matching: Rule-based matching endpoint.
- [x] Digital Contracts: Create/accept contracts.
- [x] Mock Escrow: Fund/release escrow, update trust score.
- [x] Trust Score: Default, update on completion.

## Supabase (Auth & Database)
- [ ] Schema design: Tables for users, jobs, proposals, contracts, escrow.
- [ ] Seed data: Sample users, jobs.

## Non-Functional & Demo
- [x] README.md: Setup and run instructions.
- [ ] Test locally: Run backend and open frontend.
