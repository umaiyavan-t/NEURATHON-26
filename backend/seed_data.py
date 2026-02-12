import json
import os
import datetime
import random

DATA_DIR = "data"

def write_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

regions = ["Karnataka", "Maharashtra", "Tamil Nadu", "Delhi", "Gujarat", "West Bengal", "Telangana", "Kerala", "Uttar Pradesh", "Rajasthan"]
languages = ["English", "Hindi", "Tamil", "Marathi", "Bengali", "Gujarati", "Kannada", "Telugu", "Malayalam", "Punjabi"]
skills_pool = ["Python", "FastAPI", "React", "AI", "PostgreSQL", "Figma", "Node.js", "Docker", "AWS", "Machine Learning", "Vue.js", "Spring Boot", "Kotlin", "Swift", "Graphic Design", "Content Writing", "SEO", "Blockchain", "Cybersecurity", "Terraform"]

clients = []
for i in range(1, 11):
    name = f"Client_{i}_Corp"
    region = random.choice(regions)
    clients.append({
        "id": f"user_client_{i}",
        "name": name,
        "role": "client",
        "email": f"client{i}@demo.com",
        "password": "password123",
        "company_bio": f"Focusing on {random.choice(skills_pool)} solutions in {region}.",
        "region": region,
        "languages": [random.choice(languages)]
    })

# Always include the user's specific client
clients.append({
    "name": "Sanjay",
    "role": "client",
    "email": "sanjaycvian@gmail.com",
    "password": "12345678",
    "skills": [],
    "min_rate": 0.0,
    "id": "b4b3447c-dc49-40b5-aa46-f93e47136378",
    "trust_score": 0,
    "region": "India",
    "languages": ["English", "Hindi"]
})

freelancers = []
for i in range(1, 11):
    name = f"Freelancer_{i}_Pro"
    region = random.choice(regions)
    skills = random.sample(skills_pool, 4)
    freelancers.append({
        "id": f"user_freelancer_{i}",
        "name": name,
        "role": "freelancer",
        "email": f"freelancer{i}@demo.com",
        "password": "password123",
        "skills": skills,
        "min_rate": random.randint(500, 3000),
        "languages": [random.choice(languages)],
        "region": region,
        "experience_level": random.choice(["Entry", "Intermediate", "Expert"]),
        "portfolio": [
            {"title": f"{random.choice(skills_pool)} Project", "description": f"Developed a {random.choice(skills_pool)} based solution.", "skills": random.sample(skills_pool, 2)}
        ],
        "trust_score": random.randint(60, 100),
        "github": f"https://github.com/freelancer{i}",
        "linkedin": f"https://linkedin.com/in/freelancer{i}"
    })

# Always include the user's specific freelancer
freelancers.append({
    "name": "Sanjay",
    "role": "freelancer",
    "email": "sanjaycvian1@gmail.com",
    "password": "12345678",
    "skills": ["Python", "React", "FastAPI"],
    "min_rate": 600.0,
    "id": "333dcdfc-802c-4414-8170-4b0ba9827f94",
    "trust_score": 60,
    "region": "India",
    "languages": ["English"],
    "portfolio": [
        {"title": "E-commerce Website", "description": "Built a full-stack website for a cafe with online ordering", "skills": ["React", "FastAPI"]},
        {"title": "AI Scraper", "description": "Automated data extraction from real estate sites using Selenium", "skills": ["Python", "Selenium"]}
    ],
    "skill_level": "Expert"
})

all_users = clients + freelancers

# Create Diverse Jobs
jobs = []
job_topics = [
    ("Build AI Chatbot", ["Python", "AI", "FastAPI"]),
    ("React Dashboard", ["React", "FastAPI", "PostgreSQL"]),
    ("Logo Design", ["Graphic Design", "Figma"]),
    ("Blockchain Integration", ["Blockchain", "Node.js"]),
    ("Cloud Infrastructure", ["AWS", "Docker", "Terraform"]),
    ("Mobile App UI", ["Figma", "Responsive Design"]),
    ("Python Data Scraper", ["Python", "BeautifulSoup", "Selenium"]),
    ("E-commerce Frontend", ["Vue.js", "CSS"]),
    ("Spring Boot Backend", ["Spring Boot", "PostgreSQL"]),
    ("Cybersecurity Audit", ["Cybersecurity", "Docker"])
]

for i, (title, skills) in enumerate(job_topics):
    client = random.choice(clients)
    lang = random.choice(languages)
    jobs.append({
        "id": f"job_{i+1}",
        "client_id": client["id"],
        "title": title,
        "description": f"{title} required for {client['name']}. Project focuses on {', '.join(skills)}. Please include language fit for {lang}.",
        "required_skills": skills,
        "budget": random.randint(5000, 100000),
        "timeline": f"{random.randint(1, 12)} weeks",
        "languages": [lang],
        "region": client["region"],
        "experience_required": random.choice(["Entry", "Intermediate", "Expert"]),
        "duration": f"{random.randint(1, 6)} months", # Specific requested field
        "created_at": str(datetime.datetime.now()),
        "status": "open"
    })

if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    write_json("users.json", all_users)
    write_json("jobs.json", jobs)
    write_json("proposals.json", [])
    write_json("contracts.json", [])
    print(f"Resetted and Seeded {len(all_users)} users and {len(jobs)} jobs successfully!")
