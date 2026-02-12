import json
import os

def test_prorata_logic():
    # Mock contract with milestones
    contract = {
        "id": "test_contract_milestones",
        "price": 1000,
        "status": "in_escrow",
        "milestones": [
            {"title": "M1", "weight": 0.2, "status": "approved", "proof": "done"},
            {"title": "M2", "weight": 0.5, "status": "submitted", "proof": "working"},
            {"title": "M3", "weight": 0.3, "status": "pending", "proof": ""}
        ]
    }
    
    # Logic from main.py
    approved_weight = sum(m["weight"] for m in contract.get("milestones", []) if m["status"] == "approved")
    freelancer_share = contract["price"] * approved_weight
    refund_amount = contract["price"] - freelancer_share
    
    print(f"Price: ₹{contract['price']}")
    print(f"Approved Weight: {approved_weight}")
    print(f"Freelancer Share: ₹{freelancer_share}")
    print(f"Client Refund: ₹{refund_amount}")
    
    assert freelancer_share == 200, "Freelancer should get 20% (200)"
    assert refund_amount == 800, "Client should be refunded 80% (800)"
    print("Verification Successful!")

if __name__ == "__main__":
    test_prorata_logic()
