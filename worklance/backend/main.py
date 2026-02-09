from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL : str = os.getenv("SUPABASE_URL")
SUPABASE_KEY : str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class User(BaseModel):
    id: str
    email: str
    role: str  # client or freelancer
    skills: Optional[List[str]] = []
    min_rate: Optional[int] = 0
    language: Optional[str] = "English"
    trust_score: Optional[int] = 0

class Job(BaseModel):
    title: str
    description: str
    skills: List[str]
    budget: int
    timeline: str
    client_id: str

class Proposal(BaseModel):
    job_id: str
    freelancer_id: str
    proposal_text: str
    rate: int

class Contract(BaseModel):
    job_id: str
    freelancer_id: str
    client_id: str
    scope: str
    timeline: str
    payment_terms: str
    dispute_clause: str
    accepted_by_client: bool = False
    accepted_by_freelancer: bool = False

class Escrow(BaseModel):
    contract_id: str
    status: str  # Pending, In Escrow, Released
    amount: int

@app.get("/")
def read_root():
    return {"message": "WORKLANCE API"}

# Auth endpoints (simplified, assume Supabase handles auth)
@app.post("/auth/login")
def login(email: str, password: str, role: str):
    # In real, use Supabase auth
    # For demo, return mock user
    return {"user": {"id": "1", "email": email, "role": role}}

# User profiles
@app.post("/users")
def create_user(user: User):
    # Insert into Supabase
    response = supabase.table("users").insert(user.dict()).execute()
    return response.data

@app.get("/users/{user_id}")
def get_user(user_id: str):
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    return response.data[0] if response.data else None

# Jobs
@app.post("/jobs")
def post_job(job: Job):
    response = supabase.table("jobs").insert(job.dict()).execute()
    return response.data

@app.get("/jobs")
def get_jobs():
    response = supabase.table("jobs").select("*").execute()
    return response.data

# Matching (rule-based)
@app.get("/match/{job_id}")
def match_freelancers(job_id: str):
    # Get job
    job = supabase.table("jobs").select("*").eq("id", job_id).execute().data[0]
    # Get freelancers
    freelancers = supabase.table("users").select("*").eq("role", "freelancer").execute().data
    # Simple matching: skill match, rate <= budget, language (assume English)
    matches = []
    for f in freelancers:
        if any(skill in f.get("skills", []) for skill in job["skills"]) and f.get("min_rate", 0) <= job["budget"]:
            matches.append(f)
    # Top 5
    return matches[:5]

# Proposals
@app.post("/proposals")
def submit_proposal(proposal: Proposal):
    # Check rate >= min_rate
    freelancer = supabase.table("users").select("min_rate").eq("id", proposal.freelancer_id).execute().data[0]
    if proposal.rate < freelancer["min_rate"]:
        raise HTTPException(status_code=400, detail="Rate below minimum")
    response = supabase.table("proposals").insert(proposal.dict()).execute()
    return response.data

@app.get("/proposals/{job_id}")
def get_proposals(job_id: str):
    response = supabase.table("proposals").select("*").eq("job_id", job_id).execute()
    return response.data

# Contracts
@app.post("/contracts")
def create_contract(contract: Contract):
    response = supabase.table("contracts").insert(contract.dict()).execute()
    return response.data

@app.put("/contracts/{contract_id}/accept")
def accept_contract(contract_id: str, user_id: str, role: str):
    if role == "client":
        supabase.table("contracts").update({"accepted_by_client": True}).eq("id", contract_id).execute()
    elif role == "freelancer":
        supabase.table("contracts").update({"accepted_by_freelancer": True}).eq("id", contract_id).execute()
    return {"message": "Accepted"}

# Escrow
@app.post("/escrow")
def fund_escrow(escrow: Escrow):
    response = supabase.table("escrow").insert(escrow.dict()).execute()
    return response.data

@app.put("/escrow/{escrow_id}/release")
def release_escrow(escrow_id: str):
    supabase.table("escrow").update({"status": "Released"}).eq("id", escrow_id).execute()
    # Update trust score
    contract = supabase.table("contracts").select("freelancer_id").eq("id", escrow_id).execute().data[0]
    supabase.table("users").update({"trust_score": supabase.table("users").select("trust_score").eq("id", contract["freelancer_id"]).execute().data[0]["trust_score"] + 1}).eq("id", contract["freelancer_id"]).execute()
    return {"message": "Released"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
