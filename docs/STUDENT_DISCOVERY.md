# Student Discovery & Peer Collaboration Architecture

## 1. Overview
The Student Discovery module connects students across the Centre for Artificial Intelligence and other departments at MITS Gwalior for hackathons, research projects, course study groups, and technical clubs.

Previously mocked with client-side static arrays, this capability is fully backed by PostgreSQL 18 with query optimizations and explainable match reasons in `backend/app/services/discovery_service.py`.

---

## 2. Privacy & Visibility Controls

Student privacy is strictly respected at the database query level:
1. **Self-Exclusion**: The requesting user is excluded from query results (`User.id != current_user.id`).
2. **Opt-Out & Visibility Settings**:
   - `StudentProfile.is_public == True` (if profile visibility is disabled, the student will never appear in discovery queries).
   - Sensitive contact details (personal mobile numbers, personal home addresses, confidential marks) are never returned in discovery DTOs.
3. **Verified Badge**: Students with verified student status or verified GitHub/LinkedIn credentials display an institutional verified badge.

---

## 3. Heuristic & Explainable Matching

The discovery engine scores prospective collaborators across several weighted dimensions:

| Dimension | Matching Criteria | Weight | Example Match Reason |
| :--- | :--- | :--- | :--- |
| **Skill Complementarity** | Common or complementary technical skills (e.g., PyTorch, React, NLP, Computer Vision) | 40% | *"Shares 3 skills: Python, Machine Learning, PyTorch"* |
| **Department / Batch** | Same branch (Centre for AI) or relevant batch | 25% | *"Same cohort: B.Tech Artificial Intelligence (3rd Year)"* |
| **Interests & Clubs** | Alignment in research interests (e.g., Robotics, LLMs, Competitive Coding) | 20% | *"Mutual interest in Generative AI and Hackathons"* |
| **Project Experience** | Completed projects demonstrating verified technical contributions | 15% | *"Has published projects in Deep Learning & NLP"* |

---

## 4. API Endpoints

- `GET /api/v1/students/discover`: Returns paginated, scored collaborator profiles matching optional query filters (`skills`, `branch`, `interests`, `year`).
- `GET /api/v1/students/{id}/preview`: Returns a public preview modal data structure with sanitized academic and project accomplishments.
