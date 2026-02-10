const API_URL = `http://${window.location.hostname}:8000`;

const app = {
    user: null,
    chatInterval: null,
    darkMode: localStorage.getItem("worklance_dark") === 'true',

    init: async () => {
        app.initDarkMode();
        app.startNotificationPolling();
        console.log("WorkLance Initializing...");
        console.log("Using API_URL:", API_URL);

        // Connectivity Check
        try {
            const health = await fetch(`${API_URL}/jobs`, { method: 'GET', signal: AbortSignal.timeout(3000) });
            if (!health.ok) throw new Error("Backend unreachable");
            console.log("Backend connection: OK");
        } catch (err) {
            console.error("Connectivity issue:", err);
            const msg = `❌ CONNECTION ERROR\n\nCannot reach Backend at: ${API_URL}\n\n1. Ensure the backend is running on the main laptop.\n2. Ensure both devices are on the SAME Wi-Fi.\n3. Check Windows Firewall on the main laptop.`;
            alert(msg);
            app.toast("Backend unreachable", "error");
        }

        try {
            const savedUser = localStorage.getItem("worklance_user");
            if (savedUser) {
                app.user = JSON.parse(savedUser);
                console.log("Session found for user:", app.user.email);
                if (app.user.id && !app.user.user_id) app.user.user_id = app.user.id;
                app.showDashboard();
            } else {
                console.log("No session found, showing auth.");
                app.showAuth();
            }
            app.attachListeners();
        } catch (err) {
            console.error("Init failed:", err);
            app.toast("Session error, please log in again", "error");
            app.showAuth();
        }
    },

    attachListeners: () => {
        const attach = (id, fn) => {
            const el = document.getElementById(id);
            if (el) el.onsubmit = fn;
        };
        attach("login-form", app.handleLogin);
        attach("register-form", app.handleRegister);
        attach("post-job-form", app.handlePostJob);
        attach("profile-form", app.handleUpdateProfile);

        const searchInput = document.getElementById("job-search-input");
        if (searchInput) {
            searchInput.onkeyup = (e) => { if (e.key === 'Enter') app.handleSearch(); };
        }
    },

    // --- State & Navigation ---

    hideAll: () => {
        document.querySelectorAll("main > div").forEach(div => div.classList.add("hidden"));
        document.querySelectorAll(".nav-link").forEach(l => l.classList.remove("active"));
    },

    toast: (message, type = 'success') => {
        const container = document.getElementById("toast-container");
        if (!container) return;
        const toast = document.createElement("div");
        toast.className = "toast";
        toast.style.borderLeftColor = type === 'success' ? 'var(--success)' : 'var(--error)';
        toast.innerHTML = `<span>${type === 'success' ? '✅' : '❌'}</span><span class="text-sm font-semibold">${message}</span>`;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    },

    setLoading: (loading) => {
        const loader = document.getElementById("loader");
        if (loader) loader.classList.toggle("hidden", !loading);
    },

    showAuth: () => {
        app.hideAll();
        const sidebar = document.getElementById("sidebar");
        const main = document.getElementById("main-content");
        if (sidebar) sidebar.classList.add("hidden");
        if (main) main.classList.add("main-no-sidebar");
        const authView = document.getElementById("auth-view");
        if (authView) authView.classList.remove("hidden");
        app.toggleAuth('login');
        app.setLoading(false);
    },

    toggleAuth: (view) => {
        const isLogin = view === 'login';
        const loginCard = document.getElementById("login-card");
        const regCard = document.getElementById("register-card");
        if (loginCard) loginCard.classList.toggle("hidden", !isLogin);
        if (regCard) regCard.classList.toggle("hidden", isLogin);
    },

    toggleSkillsInput: () => {
        const role = document.getElementById("reg-role").value;
        const fields = document.getElementById("freelancer-fields");
        if (fields) fields.classList.toggle("hidden", role !== 'freelancer');
    },

    showDashboard: () => {
        app.hideAll();
        app.stopChatPolling();
        const sidebar = document.getElementById("sidebar");
        const main = document.getElementById("main-content");
        if (sidebar) sidebar.classList.remove("hidden");
        if (main) main.classList.remove("main-no-sidebar");

        const navDash = document.getElementById("nav-dashboard");
        if (navDash) navDash.classList.add("active");

        if (app.user.role === 'client') {
            const dash = document.getElementById("client-dashboard");
            if (dash) dash.classList.remove("hidden");
            app.loadClientDashboard();
        } else {
            const dash = document.getElementById("freelancer-dashboard");
            if (dash) dash.classList.remove("hidden");
            app.loadFreelancerDashboard();
            app.loadFreelancerProposals();
        }
        app.renderSidebar();
    },

    renderSidebar: () => {
        const info = document.getElementById("user-info");
        if (info) info.innerText = `${app.user.name} (${app.user.role})`;

        const tsContainer = document.getElementById("trust-score-container");
        const tsDisplay = document.getElementById("trust-score-display");
        if (app.user.role === 'freelancer') {
            if (tsContainer) tsContainer.classList.remove("hidden");
            if (tsDisplay) tsDisplay.innerText = app.user.trust_score || 50;
        } else {
            if (tsContainer) tsContainer.classList.add("hidden");
        }
    },

    logout: () => {
        localStorage.removeItem("worklance_user");
        app.user = null;
        window.location.reload();
    },

    // --- Profile Management ---

    showProfile: async () => {
        app.hideAll();
        app.setLoading(true);
        try {
            document.getElementById("profile-view").classList.remove("hidden");
            document.getElementById("nav-profile").classList.add("active");

            const res = await fetch(`${API_URL}/users/${app.user.user_id}`);
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Failed to load profile");

            document.getElementById("prof-name").value = data.name || "";
            document.getElementById("prof-bio").value = data.role === 'client' ? (data.company_bio || "") : (data.bio || "");
            document.getElementById("prof-region").value = data.region || "India";

            // Populate Languages
            const langContainer = document.getElementById("prof-lang-container");
            if (langContainer) {
                const languages = data.languages || [data.language] || ["English"];
                const checks = langContainer.querySelectorAll('input[type="checkbox"]');
                checks.forEach(c => c.checked = languages.includes(c.value));
            }

            if (data.role === 'freelancer') {
                const fFields = document.getElementById("prof-freelancer-fields");
                if (fFields) fFields.classList.remove("hidden");
                document.getElementById("prof-skills").value = (data.skills || []).join(", ");
                document.getElementById("prof-rate").value = data.min_rate || 500;
                document.getElementById("prof-github").value = data.github || "";
                document.getElementById("prof-linkedin").value = data.linkedin || "";
                document.getElementById("prof-portfolio").value = data.portfolio || "";

                const resumeLink = document.getElementById("resume-view-link");
                if (data.resume_url) {
                    resumeLink.href = `${API_URL}${data.resume_url}`;
                    resumeLink.classList.remove("hidden");
                } else {
                    resumeLink.classList.add("hidden");
                }
                document.getElementById("resume-upload").onchange = app.handleResumeUpload;
            } else {
                const fFields = document.getElementById("prof-freelancer-fields");
                if (fFields) fFields.classList.add("hidden");
            }
        } catch (err) {
            app.toast(err.message, "error");
            app.showDashboard();
        } finally {
            app.setLoading(false);
        }
    },

    handleUpdateProfile: async (e) => {
        e.preventDefault();
        app.setLoading(true);
        try {
            const selectedLangs = Array.from(document.querySelectorAll('input[name="prof-lang"]:checked')).map(c => c.value);
            const payload = {
                name: document.getElementById("prof-name").value,
                languages: selectedLangs,
                region: document.getElementById("prof-region").value
            };

            if (app.user.role === 'client') {
                payload.company_bio = document.getElementById("prof-bio").value;
            } else {
                payload.skills = document.getElementById("prof-skills").value.split(",").map(s => s.trim());
                payload.min_rate = parseFloat(document.getElementById("prof-rate").value);
                payload.github = document.getElementById("prof-github").value;
                payload.linkedin = document.getElementById("prof-linkedin").value;
                payload.portfolio = document.getElementById("prof-portfolio").value;
            }

            const res = await fetch(`${API_URL}/users/${app.user.user_id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                app.user = { ...app.user, ...payload };
                localStorage.setItem("worklance_user", JSON.stringify(app.user));
                app.toast("Profile updated!");
                app.showDashboard();
            } else {
                const err = await res.json();
                app.toast(err.detail || "Update failed", "error");
            }
        } catch (err) {
            app.toast("Profile update failed", "error");
        } finally {
            app.setLoading(false);
        }
    },

    // --- Authentication ---

    handleLogin: async (e) => {
        e.preventDefault();
        app.setLoading(true);
        try {
            const email = document.getElementById("login-email").value;
            const password = document.getElementById("login-password").value;

            const res = await fetch(`${API_URL}/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();
            if (res.ok) {
                if (data.id && !data.user_id) data.user_id = data.id;
                app.user = data;
                localStorage.setItem("worklance_user", JSON.stringify(app.user));
                app.toast("Logged in successfully!");
                app.showDashboard();
            } else {
                app.toast(data.detail || "Invalid credentials", 'error');
            }
        } catch (err) {
            app.toast("Login failed", 'error');
        } finally {
            app.setLoading(false);
        }
    },

    handleRegister: async (e) => {
        e.preventDefault();
        app.setLoading(true);
        try {
            const name = document.getElementById("reg-name").value;
            const email = document.getElementById("reg-email").value;
            const password = document.getElementById("reg-password").value;
            const role = document.getElementById("reg-role").value;

            const payload = { name, email, password, role };
            if (role === 'freelancer') {
                payload.skills = document.getElementById("reg-skills").value.split(",").map(s => s.trim());
                payload.min_rate = parseFloat(document.getElementById("reg-rate").value || 500);
                payload.region = document.getElementById("reg-region").value || "India";
            }

            const res = await fetch(`${API_URL}/auth/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (res.ok) {
                app.user = { user_id: data.user_id, role, name, trust_score: role === 'freelancer' ? 50 : 0 };
                localStorage.setItem("worklance_user", JSON.stringify(app.user));
                app.toast("Welcome to WorkLance!");
                app.showDashboard();
            } else {
                app.toast(data.detail, 'error');
            }
        } catch (err) {
            app.toast("Registration failed", 'error');
        } finally {
            app.setLoading(false);
        }
    },

    // --- Dashboard Loaders ---

    loadClientDashboard: async () => {
        try {
            const [jobsRes, contractRes] = await Promise.all([
                fetch(`${API_URL}/jobs?client_id=${app.user.user_id}`),
                fetch(`${API_URL}/contracts?user_id=${app.user.user_id}`)
            ]);
            const jobs = await jobsRes.json();
            const contracts = await contractRes.json();

            // Safe update stats
            const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.innerText = val; };
            setVal("stat-active-contracts", contracts.filter(c => c.status !== 'completed').length);
            setVal("stat-active-jobs", jobs.filter(j => j.status === 'open').length);

            const projList = document.getElementById("client-active-projects");
            if (projList) {
                projList.innerHTML = "";
                contracts.filter(c => c.status !== 'completed').forEach(c => projList.appendChild(app.createContractCard(c)));
            }

            const jobList = document.getElementById("client-jobs-list");
            if (jobList) {
                jobList.innerHTML = "";
                jobs.filter(j => j.status === 'open').forEach(j => {
                    const div = document.createElement("div");
                    div.className = "card flex-between";
                    div.innerHTML = `<div><h3 class="mb-1">${j.title}</h3><span class="badge badge-open">Open</span></div><button onclick="app.viewJob('${j.id}')" class="btn btn-secondary">Proposals</button>`;
                    jobList.appendChild(div);
                });
            }
        } catch (err) {
            console.error("Client dashboard load error", err);
            app.toast("Connection failed. Check your network or firewall.", "error");
        } finally {
            app.setLoading(false);
        }
    },

    loadFreelancerDashboard: async (filterData = null) => {
        try {
            let jobs = [];
            if (filterData) {
                jobs = filterData;
            } else {
                const res = await fetch(`${API_URL}/jobs/match/${app.user.user_id}`);
                jobs = await res.json();
            }

            const contractRes = await fetch(`${API_URL}/contracts?user_id=${app.user.user_id}`);
            const contracts = await contractRes.json();

            const projList = document.getElementById("freelancer-active-projects");
            if (projList) {
                projList.innerHTML = "";
                contracts.filter(c => c.status !== 'completed').forEach(c => projList.appendChild(app.createContractCard(c)));
            }

            const list = document.getElementById("freelancer-jobs-list");
            if (list) {
                list.innerHTML = "";
                if (jobs.length === 0) list.innerHTML = `<div class="p-8 text-center text-muted">No jobs found.</div>`;
                jobs.forEach(job => {
                    const div = document.createElement("div");
                    div.className = "card";
                    div.innerHTML = `
                        <div class="flex-between mb-2">
                            <h3 style="font-size: 1.25rem;">${job.title}</h3>
                            <span class="font-bold text-primary">₹${job.budget}</span>
                        </div>
                        <p class="text-sm text-muted mb-4">${job.description.substring(0, 160)}...</p>
                        <div class="flex-between">
                            <div class="flex gap-2">
                            ${job.match_score ? `<span class="badge" style="background: #e0e7ff; color: #4338ca;">${job.match_score}% Match</span>` : ''}
                            <span class="text-xs text-muted">📍 ${job.region || 'India'}</span>
                            </div>
                            <button onclick="app.viewJob('${job.id}')" class="btn btn-primary">Apply Now</button>
                        </div>
                        ${job.match_reason ? `<div class="mt-4 pt-3 border-t text-xs italic text-success border-t" style="border-top:1px solid var(--border)">✨ ${job.match_reason}</div>` : ''}
                    `;
                    list.appendChild(div);
                });
            }
        } catch (err) {
            console.error("Freelancer dashboard load error:", err);
            app.toast("Connection failed. Check your network or firewall.", "error");
        } finally {
            app.setLoading(false);
        }
    },

    createContractCard: (c) => {
        const div = document.createElement("div");
        div.className = "card flex-between animate-slide-up hover:border-primary transition-all";
        div.style.borderLeft = "6px solid var(--primary)";
        div.style.cursor = "pointer";
        div.onclick = () => app.viewContract(c.id);

        const title = c.scope || "Professional Agreement";
        const statusClass = c.status === 'in_escrow' ? 'text-warning' : (c.status === 'completed' ? 'text-success' : 'text-primary');

        div.innerHTML = `
            <div style="flex: 1;">
                <h4 class="mb-1 font-bold text-lg">${title}</h4>
                <div class="flex items-center gap-3">
                    <span class="text-[10px] text-muted uppercase tracking-widest">${c.id}</span>
                    <span class="badge ${statusClass}">${c.status.toUpperCase()}</span>
                </div>
            </div>
            <div class="text-right">
                <p class="font-bold text-xl text-primary">₹${c.price}</p>
                <button class="btn btn-secondary mt-2 px-3 py-1 text-xs">Manage</button>
            </div>
        `;
        return div;
    },

    // --- Search & AI ---

    handleSearch: async () => {
        const q = document.getElementById("job-search-input").value;
        app.setLoading(true);
        try {
            const res = await fetch(`${API_URL}/jobs/search?q=${encodeURIComponent(q)}`);
            const data = await res.json();
            app.loadFreelancerDashboard(data);
            app.toast(`Found ${data.length} jobs`);
        } catch (err) { app.toast("Search failed", "error"); }
        finally { app.setLoading(false); }
    },

    handleEstimateCost: async () => {
        const title = document.getElementById("job-title").value;
        const description = document.getElementById("job-desc").value;
        const skills = document.getElementById("job-skills-input").value.split(",");

        if (!title || !description) return app.toast("Enter title & description first", "error");

        app.setLoading(true);
        try {
            const res = await fetch(`${API_URL}/jobs/estimate-cost`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ title, description, skills })
            });
            const data = await res.json();
            document.getElementById("job-budget").value = data.suggested_budget;
            app.toast(`AI suggests ₹${data.suggested_budget} (${data.estimated_hours}h work)`);
        } catch (err) { app.toast("Estimation failed", "error"); }
        finally { app.setLoading(false); }
    },

    // --- View Handlers ---

    showPostJob: () => {
        app.hideAll();
        const postView = document.getElementById("post-job-view");
        if (postView) postView.classList.remove("hidden");
    },

    handlePostJob: async (e) => {
        e.preventDefault();
        app.setLoading(true);
        try {
            const payload = {
                client_id: app.user.user_id,
                title: document.getElementById("job-title").value,
                description: document.getElementById("job-desc").value,
                required_skills: document.getElementById("job-skills-input").value.split(",").map(s => s.trim()),
                budget: parseFloat(document.getElementById("job-budget").value),
                timeline: "Not set",
                languages: Array.from(document.querySelectorAll('input[name="job-lang"]:checked')).map(c => c.value),
                region: document.getElementById("job-region").value
            };

            const res = await fetch(`${API_URL}/jobs`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                app.toast("Job published successfully!");
                app.showDashboard();
            } else {
                const data = await res.json();
                app.toast(data.detail || "Failed to publish", "error");
            }
        } catch (err) { app.toast("Post job failed", "error"); }
        finally { app.setLoading(false); }
    },

    viewJob: async (jobId) => {
        app.setLoading(true);
        app.hideAll();
        try {
            const detailsView = document.getElementById("job-details-view");
            if (detailsView) detailsView.classList.remove("hidden");

            const res = await fetch(`${API_URL}/jobs`);
            const jobs = await res.json();
            const job = jobs.find(j => j.id === jobId);
            if (!job) throw new Error("Job not found");

            document.getElementById("view-job-title").innerText = job.title;
            document.getElementById("view-job-desc").innerText = job.description;
            document.getElementById("view-job-budget").innerText = `₹${job.budget}`;
            document.getElementById("view-job-region").innerText = job.region || "India";

            const statusEl = document.getElementById("view-job-status");
            if (statusEl) {
                statusEl.innerText = job.status.toUpperCase();
                statusEl.className = `badge badge-${job.status}`;
            }

            if (app.user.role === 'client') {
                document.getElementById("client-proposals-section").classList.remove("hidden");
                document.getElementById("freelancer-proposal-section").classList.add("hidden");
                await app.loadProposals(jobId);
                await app.loadRecommendedTalent(jobId);
            } else {
                document.getElementById("client-proposals-section").classList.add("hidden");
                document.getElementById("freelancer-proposal-section").classList.remove("hidden");
                const warn = document.getElementById("price-warning");
                if (warn) {
                    warn.querySelector("span").innerText = app.user.min_rate || 0;
                }
                document.getElementById("proposal-form").onsubmit = (e) => app.handleSubmitProposal(e, jobId);
            }
        } catch (err) {
            app.toast(err.message, "error");
            app.showDashboard();
        } finally {
            app.setLoading(false);
        }
    },

    handleSubmitProposal: async (e, jobId) => {
        e.preventDefault();
        app.setLoading(true);
        try {
            const payload = {
                job_id: jobId,
                freelancer_id: app.user.user_id,
                price: parseFloat(document.getElementById("prop-price").value),
                timeline: document.getElementById("prop-timeline").value,
                message: document.getElementById("prop-msg").value
            };
            const res = await fetch(`${API_URL}/proposals`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                app.toast("Proposal sent!");
                app.showDashboard();
            } else {
                const err = await res.json();
                app.toast(err.detail || "Submission failed", 'error');
            }
        } catch (err) { app.toast("Proposal error", "error"); }
        finally { app.setLoading(false); }
    },

    loadRecommendedTalent: async (jobId) => {
        try {
            const res = await fetch(`${API_URL}/jobs/${jobId}/curated-freelancers`);
            const freelancers = await res.json();
            const list = document.getElementById("recommended-talent-list");
            const section = document.getElementById("recommended-talent-section");

            if (list && section) {
                if (freelancers.length > 0) {
                    section.classList.remove("hidden");
                    list.innerHTML = "";
                    freelancers.forEach(f => {
                        const div = document.createElement("div");
                        div.className = "card";
                        div.style.borderLeft = "4px solid var(--primary)";
                        div.innerHTML = `
                            <div class="flex-between">
                                <div>
                                    <h4 class="font-bold">${f.name}</h4>
                                    <div class="flex gap-2 mt-1">
                                        <span class="text-xs py-1 px-2 bg-main rounded">${f.region}</span>
                                        <span class="text-xs py-1 px-2 bg-main rounded">${(f.languages || [f.language] || ["English"]).join(', ')}</span>
                                    </div>
                                </div>
                                <div class="text-right">
                                    <div class="text-primary font-bold">${f.match_score}% Match</div>
                                    <p class="text-xs text-muted">AI Rank #1</p>
                                </div>
                            </div>
                            <div class="mt-4 flex flex-wrap gap-2">
                                ${f.skills.map(s => `<span class="tag">${s}</span>`).join('')}
                            </div>
                            <div class="mt-4 flex gap-4">
                                ${f.resume_url ? `<a href="${API_URL}${f.resume_url}" target="_blank" class="btn btn-secondary flex-1 text-sm">📄 Resume</a>` : ''}
                                <button class="btn btn-primary flex-1 text-sm" onclick="app.toast('Invitation Sent to ${f.name}!')">Invite to Job</button>
                            </div>
                        `;
                        list.appendChild(div);
                    });
                } else {
                    section.classList.add("hidden");
                }
            }
        } catch (err) { console.error("Recommended talent load error", err); }
    },

    loadProposals: async (jobId) => {
        try {
            const res = await fetch(`${API_URL}/proposals/${jobId}`);
            const proposals = await res.json();
            const list = document.getElementById("proposals-list");
            if (list) {
                list.innerHTML = proposals.length ? "" : `<p class="text-muted p-4">No proposals yet.</p>`;
                proposals.forEach(p => {
                    const div = document.createElement("div");
                    div.className = "card";
                    div.innerHTML = `
                        <div class="flex-between">
                            <div><h4 class="font-bold">${p.freelancer_name}</h4><p class="text-sm text-muted">Trust Score: ${p.freelancer_trust}</p></div>
                            <div class="text-right"><div class="font-bold text-lg">₹${p.price}</div><p class="text-xs text-muted">${p.timeline}</p></div>
                        </div>
                        <div class="mt-4 p-4 bg-main" style="border-radius: 6px;"><p class="text-sm">${p.message}</p></div>
                        <div class="flex gap-4 mt-4">
                            ${p.freelancer_resume ? `<a href="${API_URL}${p.freelancer_resume}" target="_blank" class="btn btn-secondary flex-1 text-sm">📄 View Resume</a>` : ''}
                            <button onclick="app.hireFreelancer('${p.job_id}', '${p.freelancer_id}', ${p.price})" class="btn btn-primary flex-1">Accept & Hire</button>
                        </div>
                    `;
                    list.appendChild(div);
                });
            }
        } catch (err) { console.error("Proposals load error", err); }
    },

    hireFreelancer: async (jobId, freelancerId, price) => {
        if (!confirm("Hire this freelancer?")) return;
        app.setLoading(true);
        try {
            const payload = { job_id: jobId, freelancer_id: freelancerId, client_id: app.user.user_id, price: price, scope: "Standard Project Scope", timeline: "As per proposal" };
            const res = await fetch(`${API_URL}/contracts`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                const data = await res.json();
                app.toast("Contract Generated!");
                app.viewContract(data.contract_id);
            }
        } catch (err) { app.toast("Hiring failed", "error"); }
        finally { app.setLoading(false); }
    },

    showContracts: () => {
        app.hideAll();
        app.stopChatPolling();
        app.setLoading(true);
        try {
            const listView = document.getElementById("agreements-list-view");
            if (listView) listView.classList.remove("hidden");
            const navCont = document.getElementById("nav-contracts");
            if (navCont) navCont.classList.add("active");
            app.loadAgreementsList();
        } catch (err) {
            app.toast("Failed to load agreements", "error");
        } finally {
            app.setLoading(false);
        }
    },

    loadFreelancerProposals: async () => {
        try {
            const res = await fetch(`${API_URL}/proposals/freelancer/${app.user.user_id}`);
            const proposals = await res.json();
            const list = document.getElementById("freelancer-proposals-list");
            if (list) {
                list.innerHTML = proposals.length ? "" : `<p class="text-muted p-4 card">No applications yet.</p>`;
                proposals.forEach(p => {
                    const div = document.createElement("div");
                    div.className = "card flex-between";
                    div.innerHTML = `
                        <div>
                            <h4 class="font-bold">${p.job_title}</h4>
                            <p class="text-sm text-muted">Budget: ₹${p.price} | Timeline: ${p.timeline}</p>
                        </div>
                        <span class="badge badge-${p.status}">${p.status.toUpperCase()}</span>
                    `;
                    list.appendChild(div);
                });
            }
        } catch (err) { console.error("Freelancer proposals load error", err); }
    },

    loadAgreementsList: async () => {
        try {
            const res = await fetch(`${API_URL}/contracts?user_id=${app.user.user_id}`);
            const contracts = await res.json();
            const list = document.getElementById("agreements-list");
            if (list) {
                list.innerHTML = contracts.length ? "" : `<div class="card p-12 text-center text-muted">No agreements found yet.</div>`;
                contracts.forEach(c => {
                    const div = app.createContractCard(c);
                    list.appendChild(div);
                });
            }
        } catch (err) {
            console.error("Agreements list load error", err);
        }
    },

    viewContract: async (contractId) => {
        app.setLoading(true);
        app.hideAll();
        try {
            const contractView = document.getElementById("contract-view");
            if (contractView) contractView.classList.remove("hidden");
            const navCont = document.getElementById("nav-contracts");
            if (navCont) navCont.classList.add("active");

            const res = await fetch(`${API_URL}/contracts?user_id=${app.user.user_id}`);
            const contracts = await res.json();
            const contract = contracts.find(c => c.id === contractId);
            if (!contract) throw new Error("Contract not found");

            document.getElementById("contract-text").innerText = contract.text;
            document.getElementById("contract-status-badge").innerText = contract.status.toUpperCase();
            document.getElementById("client-status").innerText = contract.client_accepted ? "✅ SIGNED" : "⌛ PENDING";
            document.getElementById("freelancer-status").innerText = contract.freelancer_accepted ? "✅ SIGNED" : "⌛ PENDING";

            const isMeClient = app.user.user_id === contract.client_id;
            const actions = document.getElementById("contract-actions");
            if (actions) {
                actions.innerHTML = "";
                const myAcceptance = isMeClient ? contract.client_accepted : contract.freelancer_accepted;

                if (!myAcceptance) {
                    actions.innerHTML = `<div class="flex items-center gap-2 mb-4"><input type="checkbox" id="agree-check"><label for="agree-check" class="text-sm">I agree to WorkLance terms.</label></div><button id="sign-btn" class="btn btn-primary" disabled>Sign Digitally</button>`;
                    const check = document.getElementById("agree-check");
                    const btn = document.getElementById("sign-btn");
                    if (check && btn) {
                        check.onchange = () => btn.disabled = !check.checked;
                        btn.onclick = async () => {
                            app.setLoading(true);
                            try {
                                await fetch(`${API_URL}/contracts/${contractId}/accept`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ contract_id: contractId, user_id: app.user.user_id }) });
                                await app.viewContract(contractId);
                            } catch (e) { app.toast("Signing failed", "error"); }
                        };
                    }
                }
            }

            const paySection = document.getElementById("payment-section");
            const relSection = document.getElementById("release-section");
            const sucSection = document.getElementById("payment-success");
            if (paySection) paySection.classList.add("hidden");
            if (relSection) relSection.classList.add("hidden");
            if (sucSection) sucSection.classList.add("hidden");

            if (isMeClient && (contract.status === 'active' || contract.status === 'in_escrow')) {
                // Determine which section to show
                if (contract.status === 'active') {
                    if (paySection) paySection.classList.remove("hidden");
                    if (relSection) relSection.classList.add("hidden");
                } else if (contract.status === 'in_escrow') {
                    if (relSection) relSection.classList.remove("hidden");
                    if (paySection) paySection.classList.add("hidden");
                }

                // Setup Cancel Button (Available in both states)
                const onCancel = async () => {
                    if (!confirm("Are you sure you want to cancel this order? This action cannot be undone.")) return;
                    app.setLoading(true);
                    try {
                        const res = await fetch(`${API_URL}/escrow/cancel/${contractId}?user_id=${app.user.user_id}`, { method: "POST" });
                        const data = await res.json();
                        if (res.ok) {
                            app.toast(data.message);
                            await app.viewContract(contractId);
                        } else {
                            throw new Error(data.detail);
                        }
                    } catch (e) { app.toast(e.message, "error"); }
                    finally { app.setLoading(false); }
                };

                const cancelBtn = document.getElementById("cancel-btn");
                const cancelBtnActive = document.getElementById("cancel-btn-active");
                if (cancelBtn) cancelBtn.onclick = onCancel;
                if (cancelBtnActive) cancelBtnActive.onclick = onCancel;

                // Setup Action Buttons
                const fundBtn = document.getElementById("fund-btn");
                if (fundBtn) fundBtn.onclick = async () => {
                    app.setLoading(true);
                    try {
                        await fetch(`${API_URL}/escrow/fund/${contractId}`, { method: "POST" });
                        app.toast("Escrow funded!");
                        await app.viewContract(contractId);
                    } catch (e) { app.toast("Funding failed", "error"); }
                };

                const relBtn = document.getElementById("release-btn");
                if (relBtn) relBtn.onclick = async () => {
                    app.setLoading(true);
                    try {
                        await fetch(`${API_URL}/escrow/release/${contractId}`, { method: "POST" });
                        app.toast("Payment released!");
                        await app.viewContract(contractId);
                    } catch (e) { app.toast("Release failed", "error"); }
                };
            } else if (contract.status === 'completed') {
                if (sucSection) sucSection.classList.remove("hidden");
            }

            // Chat UI Integration
            const chatSec = document.getElementById("chat-section");
            if (chatSec) {
                chatSec.classList.remove("hidden");
                app.loadChatHistory(contractId);
                app.startChatPolling(contractId);
            }

            // Deadline & Timer logic
            if (contract.deadline) {
                const deadlineDate = new Date(contract.deadline);
                document.getElementById("contract-deadline-display").innerText = deadlineDate.toLocaleDateString() + " " + deadlineDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

                if (app.timerInterval) clearInterval(app.timerInterval);
                app.timerInterval = setInterval(() => {
                    const now = new Date();
                    const diff = deadlineDate - now;
                    const timerEl = document.getElementById("contract-timer");
                    if (!timerEl) return;

                    if (diff > 0) {
                        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
                        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                        const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                        timerEl.innerText = `${days}d ${hours}h ${mins}m remaining`;
                        timerEl.style.color = "var(--primary)";
                    } else {
                        const delay = Math.abs(diff);
                        const days = Math.floor(delay / (1000 * 60 * 60 * 24));
                        timerEl.innerText = `OVERDUE: ${days} days late (Trust Score Impact!)`;
                        timerEl.style.color = "var(--error)";
                    }
                }, 1000);
            }
        } catch (err) {
            app.toast(err.message, "error");
            app.showDashboard();
        } finally {
            app.setLoading(false);
        }
    },

    // --- Chat Room Logic ---

    loadChatHistory: async (contractId) => {
        try {
            const res = await fetch(`${API_URL}/messages/${contractId}`);
            const messages = await res.json();
            const container = document.getElementById("chat-messages");
            if (container) {
                // Only re-render if message count changed
                if (container.children.length === messages.length) return;

                container.innerHTML = "";
                messages.forEach(m => {
                    const isMe = m.sender_id === app.user.user_id;
                    const div = document.createElement("div");
                    div.className = "chat-bubble";
                    div.style.alignSelf = isMe ? "flex-end" : "flex-start";
                    div.style.background = isMe ? "var(--primary)" : "#eee";
                    div.style.color = isMe ? "white" : "black";
                    div.style.padding = "0.75rem 1rem";
                    div.style.borderRadius = isMe ? "16px 16px 4px 16px" : "16px 16px 16px 4px";
                    div.style.maxWidth = "80%";
                    div.style.fontSize = "0.9rem";
                    div.innerText = m.text;
                    container.appendChild(div);
                });
                container.scrollTop = container.scrollHeight;
            }
        } catch (err) { console.error("Chat load error", err); }
    },

    handleSendMessage: async (e) => {
        if (e) e.preventDefault();
        const input = document.getElementById("chat-input");
        const text = input.value.trim();
        if (!text) return;

        if (!app.currentContractId) return;

        try {
            await fetch(`${API_URL}/messages`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    contract_id: app.currentContractId,
                    sender_id: app.user.user_id,
                    text: text
                })
            });
            input.value = "";
            app.loadChatHistory(app.currentContractId);
        } catch (err) { app.toast("Message failed", "error"); }
    },

    startChatPolling: (contractId) => {
        app.currentContractId = contractId;
        app.stopChatPolling();
        app.chatInterval = setInterval(() => app.loadChatHistory(contractId), 3000);
    },

    stopChatPolling: () => {
        if (app.chatInterval) clearInterval(app.chatInterval);
    },

    // --- Notifications Logic ---

    startNotificationPolling: () => {
        app.loadNotifications();
        setInterval(app.loadNotifications, 10000); // Check every 10s
    },

    loadNotifications: async () => {
        if (!app.user) return;
        try {
            const res = await fetch(`${API_URL}/notifications/${app.user.user_id}`);
            const notifs = await res.json();
            const list = document.getElementById("notif-list");
            const badge = document.getElementById("notif-badge");

            if (list) {
                const unread = notifs.filter(n => !n.read).length;
                if (badge) {
                    badge.innerText = unread;
                    badge.classList.toggle("hidden", unread === 0);
                }

                if (notifs.length === 0) {
                    list.innerHTML = `<p class="text-muted p-4 text-center text-sm">No new alerts.</p>`;
                } else {
                    list.innerHTML = "";
                    notifs.reverse().forEach(n => {
                        const div = document.createElement("div");
                        div.className = `p-3 notif-item cursor-pointer ${n.read ? 'opacity-60' : 'unread'}`;
                        div.onclick = () => app.handleNotifClick(n);
                        div.innerHTML = `
                            <p class="text-[10px] text-muted mb-1">${new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                            <h5 class="font-bold text-xs">${n.title}</h5>
                            <p class="text-xs text-muted line-clamp-2">${n.message}</p>
                        `;
                        list.appendChild(div);
                    });
                }
            }
        } catch (err) { console.error("Notif load error", err); }
    },

    toggleNotifications: () => {
        const tray = document.getElementById("notif-tray");
        if (tray) tray.classList.toggle("hidden");
    },

    handleNotifClick: async (notif) => {
        // Mark as read
        await fetch(`${API_URL}/notifications/read/${notif.id}`, { method: 'PUT' });
        app.loadNotifications();

        // Navigate if link exists
        if (notif.link) {
            if (notif.type === 'message' || notif.type === 'deadline') {
                app.viewContract(notif.link);
            } else if (notif.type === 'proposal') {
                // If it's a job link (client side)
                if (notif.link.startsWith('job_')) {
                    const jobId = notif.link.replace('job_', '');
                    app.viewJobDetails(jobId);
                } else {
                    app.viewContract(notif.link);
                }
            }
            document.getElementById("notif-tray").classList.add("hidden");
        }
    },

    clearNotifications: async () => {
        if (!app.user) return;
        try {
            await fetch(`${API_URL}/notifications/${app.user.user_id}`, { method: 'DELETE' });
            app.loadNotifications();
        } catch (err) { console.error("Clear notifs error", err); }
    },

    initDarkMode: () => {
        if (app.darkMode) {
            document.body.classList.add("dark-mode");
        }
        app.updateThemeIcon();
    },

    toggleDarkMode: () => {
        app.darkMode = !app.darkMode;
        document.body.classList.toggle("dark-mode", app.darkMode);
        localStorage.setItem("worklance_dark", app.darkMode);
        app.updateThemeIcon();
    },

    updateThemeIcon: () => {
        const icon = document.getElementById("theme-icon");
        if (!icon) return;
        if (app.darkMode) {
            // Sun icon
            icon.innerHTML = `<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>`;
        } else {
            // Moon icon
            icon.innerHTML = `<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>`;
        }
    }
};

app.init();
