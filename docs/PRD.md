# Product Requirements Document (PRD)

## Project Name

KARMIC

## Tech Stack

- HTML, CSS, JavaScript
- Python FastAPI
- Supabase

## 1. Product Overview

KARMIC is an India‑first freelance platform MVP designed to solve key problems in the Indian freelance ecosystem—unfair pricing, bidding chaos, lack of contracts, payment insecurity, and missing trust mechanisms.

The platform uses rule‑based AI logic, digital contracts, and a mock escrow payment system to ensure fair, transparent, and trust‑driven freelancing.

This PRD defines the scope for a hackathon MVP, optimized for fast development and live demo.

## 2. Goals & Objectives

### Primary Goals

- Eliminate open bidding chaos
- Protect freelancer income
- Ensure payment and delivery security
- Build long‑term trust for freelancers

### MVP Success Criteria

- Job can be posted by a client
- Freelancers are AI‑matched automatically
- Contract is generated and accepted
- Mock escrow payment is released
- Trust score is updated

## 3. Target Users

### Freelancers

- Indian freelancers (entry to mid‑level)
- Skills: Tech, Design, Content, Marketing
- Need fair pay and payment security

### Clients

- Startups, founders, individuals
- Need reliable talent with reduced risk

## 4. Problem Statements

- Unlimited bidding causes underpricing
- Freelancers face delayed or denied payments
- No formal contract clarity
- New freelancers lack visibility
- No verified trust or financial identity

## 5. Proposed Solution

KARMIC introduces:

- AI‑assisted job matching (rule‑based)
- Fair pricing enforcement
- Auto‑generated digital contracts
- Escrow‑based payment flow (mock)
- Trust score‑driven visibility

## 6. Functional Requirements

### 6.1 Authentication (Supabase)

- Email & password login
- Role selection: Client / Freelancer

### 6.2 Freelancer Module

- Create & edit profile
- Add skills, minimum rate, language
- View matched jobs
- Submit proposals

### 6.3 Client Module

- Post job with skills, budget, timeline
- View AI‑matched freelancers
- Review proposals
- Select freelancer

### 6.4 AI Matching Engine (FastAPI)

Rule‑based logic:

- Skill match
- Rate compatibility
- Language preference
- Returns top 5 freelancers only

### 6.5 Fair Pricing Guardrail

- Prevents proposals below minimum rate
- Validated at API level

### 6.6 Digital Contract System

- Auto‑generated after freelancer selection
- Includes:
  - Scope
  - Timeline
  - Payment terms
  - Dispute clause
- Must be accepted by both parties

### 6.7 Escrow Payment System (Mock)

- Client funds job into escrow (simulated)
- Payment states:
  - Pending
  - In Escrow
  - Released
- Mock UPI success flow

### 6.8 Trust Score System

- Default trust score for freelancers
- Increased after successful job completion
- Influences future matching priority

## 7. Non‑Functional Requirements

- Simple UI (HTML/CSS)
- Fast API response
- Localhost deployment
- Free‑tier only tools
- Demo‑friendly flows

## 8. Tech Stack Mapping

### Frontend

- HTML – Page structure
- CSS – Styling
- JavaScript – API calls, UI logic

### Backend

- Python FastAPI – REST APIs & business logic

### Database & Auth

- Supabase PostgreSQL
- Supabase Auth

### AI / Logic

- Rule‑based algorithms (Python)

### Payments

- Mock escrow + UPI simulation

## 9. Out of Scope (MVP)

- Real payment gateways
- Mobile apps
- Advanced ML models
- Legal e‑sign integrations

## 10. Future Enhancements

- ML‑based matching
- Freelancer credit scoring
- Milestone‑based escrow
- Regional language UI
- Tax & compliance automation