import unittest
import json
import http.client
import time

class TestWorkLanceAPI(unittest.TestCase):
    BASE_URL = "127.0.0.1:8000"
    
    def _req(self, method, endpoint, data=None):
        conn = http.client.HTTPConnection(self.BASE_URL)
        headers = {"Content-Type": "application/json"}
        body = json.dumps(data) if data else None
        conn.request(method, endpoint, body, headers)
        res = conn.getresponse()
        data = res.read()
        conn.close()
        return res.status, json.loads(data.decode("utf-8"))

    def test_full_flow(self):
        print("\n--- Testing Full Flow ---")
        
        # 1. Register Client
        print("1. Registering Client...")
        client_data = {
            "name": "Test Client",
            "role": "client",
            "email": f"client_{int(time.time())}@test.com",
            "password": "123"
        }
        status, res = self._req("POST", "/auth/register", client_data)
        self.assertEqual(status, 200)
        client_id = res["user_id"]
        print(f"   Client ID: {client_id}")

        # 2. Register Freelancer
        print("2. Registering Freelancer...")
        freelancer_email = f"free_{int(time.time())}@test.com"
        freelancer_data = {
            "name": "Test Freelancer",
            "role": "freelancer",
            "email": freelancer_email,
            "password": "123",
            "skills": ["Python", "FastAPI"],
            "min_rate": 50,
            "language": "English"
        }
        status, res = self._req("POST", "/auth/register", freelancer_data)
        self.assertEqual(status, 200)
        freelancer_id = res["user_id"]
        print(f"   Freelancer ID: {freelancer_id}")

        # 3. Post Job
        print("3. Posting Job...")
        job_data = {
            "client_id": client_id,
            "title": "Need Python Dev",
            "description": "Build backend",
            "required_skills": ["Python"],
            "budget": 500,
            "timeline": "1 week"
        }
        status, res = self._req("POST", "/jobs", job_data)
        self.assertEqual(status, 200)
        job_id = res["job_id"]
        print(f"   Job ID: {job_id}")

        # 4. Match Jobs (As Freelancer)
        print("4. Matching Jobs...")
        status, jobs = self._req("GET", f"/jobs/match/{freelancer_id}")
        self.assertEqual(status, 200)
        self.assertTrue(len(jobs) > 0)
        self.assertEqual(jobs[0]["id"], job_id)
        print("   Job found in matches!")

        # 5. Submit Proposal
        print("5. Submitting Proposal...")
        prop_data = {
            "job_id": job_id,
            "freelancer_id": freelancer_id,
            "price": 400,
            "timeline": "5 days",
            "message": "I can do it."
        }
        status, res = self._req("POST", "/proposals", prop_data)
        self.assertEqual(status, 200)
        proposal_id = res["proposal_id"]
        print(f"   Proposal ID: {proposal_id}")

        # 6. View Proposals (As Client)
        print("6. Viewing Proposals...")
        status, props = self._req("GET", f"/proposals/{job_id}")
        self.assertEqual(status, 200)
        self.assertTrue(any(p["id"] == proposal_id for p in props))
        print("   Proposal visible to client.")
        
        # 7. Create Contract
        print("7. Creating Contract...")
        contract_data = {
            "job_id": job_id,
            "freelancer_id": freelancer_id,
            "client_id": client_id,
            "price": 400,
            "scope": "Dev work",
            "timeline": "5 days"
        }
        status, res = self._req("POST", "/contracts", contract_data)
        self.assertEqual(status, 200)
        contract_id = res["contract_id"]
        print(f"   Contract ID: {contract_id}")

        # 8. Accept Contract (Client)
        print("8. Client Accepting Contract...")
        status, res = self._req("PUT", f"/contracts/{contract_id}/accept", {"contract_id": contract_id, "user_id": client_id})
        self.assertEqual(status, 200)
        
        # 9. Accept Contract (Freelancer)
        print("9. Freelancer Accepting Contract...")
        status, res = self._req("PUT", f"/contracts/{contract_id}/accept", {"contract_id": contract_id, "user_id": freelancer_id})
        self.assertEqual(status, 200)
        
        # 10. Check Contract Status
        print("10. Checking Active Status...")
        status, contracts = self._req("GET", f"/contracts?user_id={client_id}")
        target = next(c for c in contracts if c["id"] == contract_id)
        self.assertEqual(target["status"], "active")
        print("    Contract is ACTIVE.")

if __name__ == '__main__':
    unittest.main()
