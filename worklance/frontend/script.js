const API_BASE = 'http://localhost:8000';

let currentUser = null;

function showLogin() {
    document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
    document.getElementById('login').classList.remove('hidden');
}

function showClient() {
    if (!currentUser || currentUser.role !== 'client') return;
    document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
    document.getElementById('client').classList.remove('hidden');
    loadJobs();
}

function showFreelancer() {
    if (!currentUser || currentUser.role !== 'freelancer') return;
    document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
    document.getElementById('freelancer').classList.remove('hidden');
    loadMatchedJobs();
}

function showPostJob() {
    document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
    document.getElementById('post-job').classList.remove('hidden');
}

function showProfile() {
    document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
    document.getElementById('profile').classList.remove('hidden');
}

async function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const role = document.getElementById('role').value;
    const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, role })
    });
    const data = await response.json();
    currentUser = data.user;
    if (role === 'client') showClient();
    else showFreelancer();
}

async function postJob() {
    const title = document.getElementById('job-title').value;
    const description = document.getElementById('job-desc').value;
    const skills = document.getElementById('job-skills').value.split(',');
    const budget = parseInt(document.getElementById('job-budget').value);
    const timeline = document.getElementById('job-timeline').value;
    await fetch(`${API_BASE}/jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description, skills, budget, timeline, client_id: currentUser.id })
    });
    showClient();
}

async function updateProfile() {
    const skills = document.getElementById('skills').value.split(',');
    const min_rate = parseInt(document.getElementById('min-rate').value);
    const language = document.getElementById('language').value;
    await fetch(`${API_BASE}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: currentUser.id, email: currentUser.email, role: currentUser.role, skills, min_rate, language, trust_score: 0 })
    });
    showFreelancer();
}

async function loadJobs() {
    const response = await fetch(`${API_BASE}/jobs`);
    const jobs = await response.json();
    const list = document.getElementById('jobs-list');
    list.innerHTML = jobs.map(j => `<div>${j.title} - ${j.budget}</div>`).join('');
}

async function loadMatchedJobs() {
    // For simplicity, assume all jobs are matched
    const response = await fetch(`${API_BASE}/jobs`);
    const jobs = await response.json();
    const list = document.getElementById('matched-jobs');
    list.innerHTML = jobs.map(j => `<div>${j.title} <button onclick="submitProposal('${j.id}')">Propose</button></div>`).join('');
}

async function submitProposal(jobId) {
    const rate = prompt('Enter your rate:');
    await fetch(`${API_BASE}/proposals`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_id: jobId, freelancer_id: currentUser.id, proposal_text: 'Proposal', rate: parseInt(rate) })
    });
}
