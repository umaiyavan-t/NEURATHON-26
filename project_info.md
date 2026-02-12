# WorkLance: Project Info & Feature Directory 🚀

WorkLance is a premium, AI-driven freelance ecosystem designed for security, trust, and advanced talent matching. This document provides a comprehensive list of every feature currently implemented in the platform.

---

## 🧠 AI & Intelligent Matching

### 1. Refined Talent Scout (Semantic Matcher)
The platform uses a custom semantic matching engine that goes beyond simple keyword searches. It evaluates:
- **Portfolio Similarity (25%)**: Analyzes freelancer portfolio items against job descriptions.
- **Skill Alignment (40%)**: Projects weighted scores for technical fit.
- **Trust Context (15%)**: Incorporates historical reliability.
- **Localization (10%)**: Matches region and language preferences.
- **Matching Reasons**: Every recommendation includes a natural language "AI Reason" explaining the match.

### 2. AI Resume Scanner
- **PDF Analysis**: Integrated `PyPDF2` to read uploaded freelancer resumes.
- **Skill Extraction**: Automatically detects technical skills from resumes to pre-fill profiles.
- **AI Ranking**: Assigns "Expert" or "Intermediate" badges based on resume density and depth.

### 3. AI Cost Estimator
- **Dynamic Pricing**: Clients receive a suggested budget and estimated project hours based on the job title, description, and required skills during the posting phase.

---

## 🛡️ Trust & Security (Karmic System)

### 4. Trust Score Ecosystem
- **Historical Reliability**: Every freelancer and client has a Trust Score that fluctuates based on completion rates and feedback.
- **Priority Ranking**: High-trust users are prioritized in AI matchmaking results.

### 5. Watermarked Media Proofs
- **Screenshot Protection**: Freelancers can upload image-based "Proof of Work" for milestones.
- **Automated Processing**: Integrated `Pillow` (PIL) to automatically apply a semi-transparent "WORKLANCE PROOF" watermark to all uploaded media.
- **Protected Preview**: A secure modal renders proofs for clients while blocking right-clicks and easy downloads.

### 6. Mutual Milestone Agreement
- **The Handshake**: Before work begins, both the client and freelancer must "Agree to Plan" via a dedicated UI handshake.
- **Agreement Lockdown**: Milestone submissions are blocked until mutual consent is recorded on the contract.

---

## 💰 Escrow & Financials

### 7. Milestone-Based Progress
- **Weighted Stages**: Projects are broken down into milestones with specific weights (e.g., 20% Kickoff, 50% Core, 30% Final).
- **Execution Bar**: A visual progress bar in the contract view updates dynamically as milestones are approved.

### 8. Pro-rata Refund Logic
- **Fair Cancellation**: If a project is cancelled mid-way, the system automatically calculates the split.
- **Milestone Guard**: Funds are released to the freelancer based on the sum of weights of *approved* milestones, with the remainder refunded to the client.

### 9. Stripe Escrow Integration
- **Stripe Checkout**: Fully integrated `Stripe.js` flow for funding contracts.
- **Automated Workflow**: Contracts automatically move from 'active' to 'in_escrow' upon successful Stripe verification.

---

## 🔍 Discovery & Search

### 10. Advanced Dynamic Filters
- **Multidimensional Filter Sidebar**: Freelancers can filter the global job market by:
  - Budget Range (Min/Max ₹)
  - Region (State-specific)
  - Specific Tech Skills
- **Talent Search (Client Side)**: Clients can search for specific freelancers using the same advanced parameters.

---

## 💬 Communication & Notifications

### 11. Local Private Chatroom
- **Contract Context**: Every contract has a built-in private chat area.
- **Context Preservation**: Messages are stored locally per contract to maintain a full history of the project discussion.

### 12. Real-Time Notification System
- **Event-Driven Alerts**: Users receive instant notifications for:
  - New contract proposals.
  - Milestone approvals.
  - New chat messages.
  - Milestone agreement requests.
  - Payment successes.

---

## 🎨 UI/UX & Accessibility

### 13. High-Contrast Design System
- **Accessibility Standard**: Standardized color palette for maximum readability (Royal Blue accents on architectural grays/blacks).
- **Theme-Aware Logic**: Toasts, loaders, and modals automatically adjust contrast based on the active theme.

### 14. OLED Dark Mode
- **Pitch-Black Experience**: A specialized high-performance dark mode for reduced eye strain and high energy efficiency.

### 15. Real-Time Project Timers
- **Deadline Tracking**: Countdown timers in the contract view help monitor project health and proximity to deadlines.

---

## 🛠️ Technical Specifications
- **Framework**: FastAPI (Backend), Vanilla JS/CSS (Frontend).
- **Storage**: Persistent JSON-based data layer.
- **Libraries**: `Stripe`, `Pillow` (Watermarking), `PyPDF2` (Resumes).
- **Network**: Cross-device connectivity support (0.0.0.0 binding).
