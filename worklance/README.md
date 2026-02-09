# WORKLANCE MVP

India-first freelance platform MVP to solve unfair pricing, bidding chaos, lack of contracts, payment insecurity, and missing trust mechanisms.

## Tech Stack
- Frontend: HTML, CSS, JS
- Backend: Python FastAPI
- Database/Auth: Supabase

## Setup

1. Install Python 3.8+
2. `cd backend`
3. `pip install -r requirements.txt`
4. Set environment variables: SUPABASE_URL, SUPABASE_KEY
5. `python main.py`
6. Open frontend/index.html in browser

## Supabase Setup
- Create project on Supabase
- Create tables: users, jobs, proposals, contracts, escrow
- Schema:
  - users: id, email, role, skills (json), min_rate, language, trust_score
  - jobs: id, title, description, skills (json), budget, timeline, client_id
  - proposals: id, job_id, freelancer_id, proposal_text, rate
  - contracts: id, job_id, freelancer_id, client_id, scope, timeline, payment_terms, dispute_clause, accepted_by_client, accepted_by_freelancer
  - escrow: id, contract_id, status, amount

## Demo Flow
1. Login as client, post job
2. Login as freelancer, view matched jobs, submit proposal
3. Client selects freelancer, contract generated
4. Both accept contract
5. Client funds escrow, freelancer completes job, escrow released, trust score updated
