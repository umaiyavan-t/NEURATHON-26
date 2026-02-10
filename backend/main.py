from fastapi import FastAPI, HTTPException, Body, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import re
import datetime
import json
import os
import shutil

# --- Utils ---
from utils import read_json, append_json, write_json, get_by_id, update_json

def slugify(text: str) -> str:
    return re.sub(r'[\W_]+', '_', text.lower()).strip('_')

app = FastAPI(title="WorkLance API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
UPLOAD_DIR = "uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# --- Models ---
class UserRegister(BaseModel):
    name: str
    role: str # "client" or "freelancer"
    email: str
    password: str
    skills: List[str] = []
    min_rate: float = 0.0
    languages: List[str] = ["English"]
    region: str = "India" # e.g., "Karnataka", "Maharashtra"
    experience_level: str = "Intermediate" # "Entry", "Intermediate", "Expert"

class UserUpdate(BaseModel):
    name: Optional[str] = None
    skills: Optional[List[str]] = None
    min_rate: Optional[float] = None
    languages: Optional[List[str]] = None
    region: Optional[str] = None
    experience_level: Optional[str] = None
    company_bio: Optional[str] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class ChatMessage(BaseModel):
    contract_id: str
    sender_id: str
    text: str
    timestamp: str = str(datetime.datetime.now())

class JobCreate(BaseModel):
    client_id: str
    title: str
    description: str
    required_skills: List[str]
    budget: float
    timeline: str
    languages: List[str] = ["English"]
    region: str = "India"
    experience_required: str = "Intermediate"

class CostEstimateRequest(BaseModel):
    title: str
    description: str
    skills: List[str]

class ProposalCreate(BaseModel):
    job_id: str
    freelancer_id: str
    price: float
    timeline: str
    message: str

class ContractCreate(BaseModel):
    job_id: str
    freelancer_id: str
    client_id: str
    price: float
    scope: str
    timeline: str
    deadline_days: int = 7

class AcceptContract(BaseModel):
    contract_id: str
    user_id: str # Who is accepting

class Notification(BaseModel):
    id: Optional[str] = None
    user_id: str
    title: str
    message: str
    type: str # "message", "proposal", "deadline"
    link: Optional[str] = None
    read: bool = False
    created_at: str = str(datetime.datetime.now())

def create_notification(user_id: str, title: str, message: str, type: str, link: Optional[str] = None):
    notif = Notification(
        id=f"notif_{int(datetime.datetime.now().timestamp())}_{user_id[-4:]}",
        user_id=user_id,
        title=title,
        message=message,
        type=type,
        link=link
    )
    append_json("notifications.json", notif.dict())

# --- Routes: Auth ---

@app.post("/auth/register")
def register(user: UserRegister):
    users = read_json("users.json")
    for u in users:
        if u["email"] == user.email:
            raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = user.dict()
    slug = slugify(user.name)
    new_user["id"] = f"user_{slug}"
    
    # Check for ID collision (simple approach)
    existing = get_by_id("users.json", new_user["id"])
    if existing:
        new_user["id"] += f"_{int(datetime.datetime.now().timestamp())}"

    new_user["trust_score"] = 50 if user.role == "freelancer" else 0
    
    append_json("users.json", new_user)
    
    if user.role == "freelancer":
        append_json("trust_scores.json", {
            "user_id": new_user["id"], 
            "score": 50, 
            "history": []
        })

    return {"message": "User registered", "user_id": new_user["id"], "role": new_user["role"]}

@app.post("/auth/login")
def login(creds: UserLogin):
    email = creds.email.strip().lower()
    users = read_json("users.json")
    for u in users:
        if u["email"].strip().lower() == email and u["password"] == creds.password:
            return {
                "user_id": u["id"], 
                "name": u["name"], 
                "role": u["role"], 
                "skills": u.get("skills", []), 
                "min_rate": u.get("min_rate", 0),
                "trust_score": u.get("trust_score", 0),
                "region": u.get("region", "India"),
                "languages": u.get("languages", ["English"])
            }
    raise HTTPException(status_code=401, detail="Invalid credentials")

# --- Routes: User Profiles ---

@app.get("/users/{user_id}")
def get_user_profile(user_id: str):
    user = get_by_id("users.json", user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Don't return password
    safe_user = {k: v for k, v in user.items() if k != "password"}
    return safe_user

@app.put("/users/{user_id}")
def update_user_profile(user_id: str, data: UserUpdate):
    users = read_json("users.json")
    for u in users:
        if u["id"] == user_id:
            update_dict = data.dict(exclude_unset=True)
            u.update(update_dict)
            write_json("users.json", users)
            return {"message": "Profile updated", "user": {k: v for k, v in u.items() if k != "password"}}
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/users/{user_id}/resume")
async def upload_resume(user_id: str, resume: UploadFile = File(...)):
    if resume.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    file_ext = resume.filename.split(".")[-1]
    filename = f"resume_{user_id}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)
    
    resume_url = f"/uploads/resumes/{filename}"
    
    # Update user in json
    users = read_json("users.json")
    for u in users:
        if u["id"] == user_id:
            u["resume_url"] = resume_url
            write_json("users.json", users)
            return {"message": "Resume uploaded", "resume_url": resume_url}
            
    raise HTTPException(status_code=404, detail="User not found")

# --- Routes: Jobs ---

@app.post("/jobs")
def create_job(job: JobCreate):
    new_job = job.dict()
    slug = slugify(job.title)
    new_job["id"] = f"job_{slug}"
    
    # Simple collision handling
    if get_by_id("jobs.json", new_job["id"]):
        new_job["id"] += f"_{int(datetime.datetime.now().timestamp())}"

    new_job["created_at"] = str(datetime.datetime.now())
    new_job["status"] = "open"
    append_json("jobs.json", new_job)
    return {"message": "Job posted", "job_id": new_job["id"]}

@app.get("/jobs")
def list_jobs(client_id: Optional[str] = None):
    jobs = read_json("jobs.json")
    if client_id:
        return [j for j in jobs if j["client_id"] == client_id]
    return jobs

@app.get("/jobs/match/{freelancer_id}")
def match_jobs(freelancer_id: str):
    freelancer = get_by_id("users.json", freelancer_id)
    if not freelancer or freelancer["role"] != "freelancer":
        raise HTTPException(status_code=404, detail="Freelancer not found")
    
    jobs = read_json("jobs.json")
    open_jobs = [j for j in jobs if j["status"] == "open"]
    
    scored_jobs = []
    f_skills = set(s.lower() for s in freelancer.get("skills", []))
    f_lang = freelancer.get("language", "English").lower()
    f_region = freelancer.get("region", "India").lower()
    f_rate = freelancer.get("min_rate", 0)
    
    for job in open_jobs:
        j_skills = set(s.lower() for s in job.get("required_skills", []))
        j_langs = [l.lower() for l in job.get("languages", [job.get("language", "English")])]
        j_region = job.get("region", "India").lower()
        j_budget = job.get("budget", 0)
        
        # 1. Skill Match (50%)
        overlap = f_skills.intersection(j_skills)
        skill_score = (len(overlap) / len(j_skills)) if j_skills else 0
        
        # 2. Trust Score (20%)
        trust_weight = (freelancer.get("trust_score", 50) / 100)
        
        # 3. Language Match (15%)
        f_langs = [l.lower() for l in freelancer.get("languages", [freelancer.get("language", "English")])]
        lang_overlap = set(f_langs).intersection(set(j_langs))
        lang_score = 1.0 if lang_overlap else 0.2
        
        # 4. Region Match (10%)
        region_score = 1.0 if f_region == j_region else (0.5 if "india" in f_region and "india" in j_region else 0.2)
        
        # 5. Rate Fit (5%)
        rate_fit = 1.0 if j_budget >= f_rate else (0.5 if j_budget >= (f_rate * 0.8) else 0.1)
        
        total_score = (skill_score * 0.5) + (trust_weight * 0.2) + (lang_score * 0.15) + (region_score * 0.1) + (rate_fit * 0.05)
        
        if skill_score > 0: 
            scored_jobs.append({
                "job": job,
                "score": round(total_score * 100, 1),
                "matched_skills": list(overlap)
            })
    
    scored_jobs.sort(key=lambda x: x["score"], reverse=True)
    
    # Enrich job with match score for UI
    results = []
    for item in scored_jobs[:10]:
        job_copy = item["job"].copy()
        job_copy["match_score"] = item["score"]
        job_copy["match_reason"] = f"Matches your {len(item['matched_skills'])} skills & region fit."
        results.append(job_copy)
        
    return results

@app.get("/jobs/{job_id}/curated-freelancers")
def get_curated_freelancers(job_id: str):
    job = get_by_id("jobs.json", job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    users = read_json("users.json")
    freelancers = [u for u in users if u["role"] == "freelancer"]
    
    scored_freelancers = []
    j_skills = set(s.lower() for s in job.get("required_skills", []))
    j_langs = [l.lower() for l in job.get("languages", [job.get("language", "English")])]
    j_region = job.get("region", "India").lower()
    
    for f in freelancers:
        f_skills = set(s.lower() for s in f.get("skills", []))
        f_langs = [l.lower() for l in f.get("languages", [f.get("language", "English")])]
        f_region = f.get("region", "India").lower()
        
        # 1. Skill Match (50%)
        overlap = f_skills.intersection(j_skills)
        skill_score = (len(overlap) / len(j_skills)) if j_skills else 0
        
        # 2. Trust Score (20%)
        trust_weight = (f.get("trust_score", 50) / 100)
        
        # 3. Language Match (15%)
        lang_overlap = set(f_langs).intersection(set(j_langs))
        lang_score = 1.0 if lang_overlap else 0.2
        
        # 4. Region Match (15%)
        region_score = 1.0 if f_region == j_region else (0.5 if "india" in f_region and "india" in j_region else 0.2)
        
        total_score = (skill_score * 0.5) + (trust_weight * 0.2) + (lang_score * 0.15) + (region_score * 0.15)
        
        if skill_score > 0 or lang_overlap:
            f_copy = {k: v for k, v in f.items() if k != "password"}
            f_copy["match_score"] = round(total_score * 100, 1)
            scored_freelancers.append(f_copy)
            
    scored_freelancers.sort(key=lambda x: x["match_score"], reverse=True)
    return scored_freelancers[:5]

@app.get("/jobs/search")
def search_jobs(q: str = "", skills: str = "", min_budget: float = 0.0):
    jobs = read_json("jobs.json")
    open_jobs = [j for j in jobs if j["status"] == "open"]
    
    results = []
    q = q.lower()
    filter_skills = [s.strip().lower() for s in skills.split(",")] if skills else []
    
    for job in open_jobs:
        match = True
        if q and q not in job["title"].lower() and q not in job["description"].lower():
            match = False
        if filter_skills:
            j_skills = [s.lower() for s in job["required_skills"]]
            if not any(s in j_skills for s in filter_skills):
                match = False
        if job["budget"] < min_budget:
            match = False
            
        if match:
            results.append(job)
            
    return results

@app.post("/jobs/estimate-cost")
def estimate_cost(req: CostEstimateRequest):
    # Base rate ₹800/hr
    base_rate = 800
    
    high_pay_skills = ["ai", "ml", "fastapi", "react", "blockchain", "expert"]
    multiplier = 1.0
    
    for skill in req.skills:
        if skill.lower() in high_pay_skills:
            multiplier += 0.3
            
    # Estimate hours based on description length (rough)
    words = len(req.description.split())
    estimated_hours = max(5, words / 10) # 10 words per hour? tiny logic
    
    suggested_budget = round(estimated_hours * base_rate * multiplier, -2) # Round to nearest 100
    
    return {
        "suggested_budget": suggested_budget,
        "estimated_hours": round(estimated_hours, 1),
        "multiplier_applied": round(multiplier, 2)
    }

# --- Routes: Proposals ---

@app.post("/proposals")
def submit_proposal(proposal: ProposalCreate):
    freelancer = get_by_id("users.json", proposal.freelancer_id)
    if not freelancer: 
        raise HTTPException(status_code=404, detail="Freelancer not found")
        
    # Fair Pricing Guardrail
    if proposal.price < freelancer.get("min_rate", 0):
        raise HTTPException(status_code=400, detail=f"Proposal price cannot be lower than your minimum rate (₹{freelancer.get('min_rate')})")
    
    new_proposal = proposal.dict()
    new_proposal["id"] = f"prop_{proposal.freelancer_id}_{proposal.job_id}"
    new_proposal["status"] = "pending"
    append_json("proposals.json", new_proposal)

    # Notify Client
    job = get_by_id("jobs.json", proposal.job_id)
    if job:
        create_notification(
            user_id=job["client_id"],
            title="New Proposal Received",
            message=f"{freelancer['name']} applied to '{job['title']}'",
            type="proposal",
            link=f"job_{job['id']}"
        )

    return {"message": "Proposal submitted", "proposal_id": new_proposal["id"]}

@app.get("/proposals/{job_id}")
def get_proposals(job_id: str):
    proposals = read_json("proposals.json")
    # Enrich with freelancer name for client view
    job_proposals = [p for p in proposals if p["job_id"] == job_id]
    for p in job_proposals:
        f = get_by_id("users.json", p["freelancer_id"])
        if f:
            p["freelancer_name"] = f["name"]
            p["freelancer_trust"] = f.get("trust_score", 50)
            p["freelancer_resume"] = f.get("resume_url")
    return job_proposals

# --- Routes: Contracts ---

@app.post("/contracts")
def create_contract(contract: ContractCreate):
    new_contract = contract.dict()
    new_contract["id"] = f"contract_{contract.job_id}_{contract.freelancer_id[:8]}"
    new_contract["status"] = "draft"
    new_contract["client_accepted"] = False
    new_contract["freelancer_accepted"] = False
    new_contract["created_at"] = str(datetime.datetime.now())
    
    # Calculate deadline
    deadline_date = datetime.datetime.now() + datetime.timedelta(days=contract.deadline_days)
    new_contract["deadline"] = str(deadline_date)
    
    # Professional Text with Names
    client = get_by_id("users.json", contract.client_id)
    freelancer = get_by_id("users.json", contract.freelancer_id)
    c_name = client["name"] if client else "Client"
    f_name = freelancer["name"] if freelancer else "Freelancer"
    
    new_contract["text"] = f"""
AGREEMENT FOR SERVICES

This Professional Services Agreement is entered into between {c_name} (the "Client") and {f_name} (the "Freelancer").

1. SCOPE OF WORK: {contract.scope}
2. COMPENSATION: The total fee for this project is ₹{contract.price}.
3. DEADLINE: Work must be completed by {deadline_date.strftime('%Y-%m-%d')}.
4. LATE DELIVERY TERMS: In the event of late delivery, the total compensation may be subject to a 5% reduction per 24-hour delay, subject to negotiation between the parties.
5. QUALITY ASSURANCE: Freelancer guarantees professional quality in line with the job description.

Digitally signed and recorded on WorkLance.
"""
    append_json("contracts.json", new_contract)

    # Update Job Status so it disappears from 'Open' matching
    jobs = read_json("jobs.json")
    for j in jobs:
        if j["id"] == contract.job_id:
            j["status"] = "in_progress"
            break
    write_json("jobs.json", jobs)

    return {"message": "Contract generated", "contract_id": new_contract["id"]}

@app.get("/contracts")
def list_contracts(user_id: str):
    contracts = read_json("contracts.json")
    return [c for c in contracts if c["client_id"] == user_id or c["freelancer_id"] == user_id]

@app.put("/contracts/{contract_id}/accept")
def accept_contract(payload: AcceptContract):
    contract = get_by_id("contracts.json", payload.contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    update_data = {}
    if payload.user_id == contract["client_id"]:
        update_data["client_accepted"] = True
    elif payload.user_id == contract["freelancer_id"]:
        update_data["freelancer_accepted"] = True
    else:
        raise HTTPException(status_code=403, detail="User not part of contract")

    # Check if both accepted
    # We need to apply the update first to check the new state
    # But read_json returns a snapshot.
    # Logic: if the OTHER party already accepted, or if we just updated it.
    
    is_client = payload.user_id == contract["client_id"]
    other_accepted = contract["freelancer_accepted"] if is_client else contract["client_accepted"]
    
    if other_accepted:
        update_data["status"] = "active"
    
    # Perform update
    # Need to update specific fields. My utils update_json is a bit simple, replaces fields.
    # It updates fields in the dict.
    
    # Let's do it manually via logic to ensure we don't overwrite blindly
    contracts = read_json("contracts.json")
    for c in contracts:
        if c["id"] == payload.contract_id:
            if is_client: c["client_accepted"] = True
            else: c["freelancer_accepted"] = True
            
            if c["client_accepted"] and c["freelancer_accepted"]:
                c["status"] = "active"
            
            write_json("contracts.json", contracts)
            
            # Notify other party
            other_party = c["freelancer_id"] if payload.user_id == c["client_id"] else c["client_id"]
            party_role = "Client" if payload.user_id == c["client_id"] else "Freelancer"
            create_notification(
                user_id=other_party,
                title="Agreement Signed",
                message=f"The {party_role} has signed the contract for job '{c.get('job_id', 'Unknown')}'.",
                type="proposal",
                link=payload.contract_id
            )
            return {"message": "Contract accepted"}
    
    raise HTTPException(status_code=404, detail="Contract not found")

# --- Routes: Escrow & Trust ---

@app.post("/escrow/fund/{contract_id}")
def fund_escrow(contract_id: str):
    contracts = read_json("contracts.json")
    for c in contracts:
        if c["id"] == contract_id:
            if c["status"] != "active":
                raise HTTPException(status_code=400, detail="Contract must be active (accepted by both) to fund.")
            c["status"] = "in_escrow"
            write_json("contracts.json", contracts)
            return {"message": "Escrow funded via Mock Payment"}
    raise HTTPException(status_code=404, detail="Contract not found")

@app.post("/escrow/release/{contract_id}")
def release_payment(contract_id: str):
    contracts = read_json("contracts.json")
    target_contract = None
    for c in contracts:
        if c["id"] == contract_id:
            target_contract = c
            if c["status"] != "in_escrow":
                raise HTTPException(status_code=400, detail="Funds not in escrow.")
            c["status"] = "completed"
            
            # Update Job Status to completed as well
            jobs = read_json("jobs.json")
            for j in jobs:
                if j["id"] == c["job_id"]:
                    j["status"] = "completed"
                    break
            write_json("jobs.json", jobs)
            break
            
    if target_contract:
        write_json("contracts.json", contracts)
        
        # Calculate Late Penalty & Trust Impact
        fid = target_contract["freelancer_id"]
        deadline = datetime.datetime.fromisoformat(target_contract.get("deadline", str(datetime.datetime.now())))
        now = datetime.datetime.now()
        
        trust_bonus = 10
        penalty_msg = ""
        
        if now > deadline:
            delay = now - deadline
            days_late = delay.days + (1 if delay.seconds > 0 else 0)
            trust_bonus = max(-20, 10 - (days_late * 5)) # Heavily penalize trust
            
            # Suggest cost reduction logic (for UI/client discretion, but we log it)
            suggested_reduction = min(0.5, days_late * 0.05) # Max 50%
            final_payout = target_contract["price"] * (1 - suggested_reduction)
            penalty_msg = f" (Late by {days_late} days. Suggested payout: ₹{final_payout})"

        # Update Trust Score
        users = read_json("users.json")
        for u in users:
            if u["id"] == fid:
                u["trust_score"] = max(0, min(100, u.get("trust_score", 50) + trust_bonus))
                break
        write_json("users.json", users)
        
        # Notify Freelancer
        create_notification(
            user_id=fid,
            title="Payment Released! 🎉",
            message=f"₹{target_contract['price']} has been released to your account{penalty_msg}.",
            type="deadline",
            link=contract_id
        )

        return {"message": f"Payment released{penalty_msg}. Trust Score changed by {trust_bonus}."}
        
    raise HTTPException(status_code=404, detail="Contract not found")

@app.get("/proposals/freelancer/{freelancer_id}")
def get_freelancer_proposals(freelancer_id: str):
    proposals = read_json("proposals.json")
    f_proposals = [p for p in proposals if p["freelancer_id"] == freelancer_id]
    
    # Enrich with job title
    jobs = read_json("jobs.json")
    for p in f_proposals:
        job = next((j for j in jobs if j["id"] == p["job_id"]), None)
        if job:
            p["job_title"] = job["title"]
            p["job_status"] = job["status"]
            
    return f_proposals

# --- Routes: Chat ---

@app.post("/messages")
def send_message(msg: ChatMessage):
    append_json("messages.json", msg.dict())
    
    # Notify recipient
    contract = get_by_id("contracts.json", msg.contract_id)
    if contract:
        recipient_id = contract["freelancer_id"] if msg.sender_id == contract["client_id"] else contract["client_id"]
        sender = get_by_id("users.json", msg.sender_id)
        sender_name = sender["name"] if sender else "Someone"
        
        create_notification(
            user_id=recipient_id,
            title="New Message",
            message=f"{sender_name}: {msg.text[:50]}...",
            type="message",
            link=msg.contract_id
        )

    return {"message": "Message sent"}

@app.get("/messages/{contract_id}")
def get_messages(contract_id: str):
    messages = read_json("messages.json")
    return [m for m in messages if m["contract_id"] == contract_id]

# --- Routes: Notifications ---

@app.get("/notifications/{user_id}")
def get_notifications(user_id: str):
    notifs = read_json("notifications.json")
    return [n for n in notifs if n["user_id"] == user_id]

@app.put("/notifications/read/{notif_id}")
def mark_notif_read(notif_id: str):
    notifs = read_json("notifications.json")
    for n in notifs:
        if n["id"] == notif_id:
            n["read"] = True
            break
    write_json("notifications.json", notifs)
    return {"message": "Notification marked as read"}

@app.delete("/notifications/{user_id}")
def clear_notifications(user_id: str):
    notifs = read_json("notifications.json")
    remaining = [n for n in notifs if n["user_id"] != user_id]
    write_json("notifications.json", remaining)
    return {"message": "Notifications cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
