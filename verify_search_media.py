import requests
import os
import io
from PIL import Image

API_URL = "http://localhost:8000"

def test_search():
    print("Testing Search...")
    # Test Job Search
    res = requests.get(f"{API_URL}/jobs/search?min_budget=1000&max_budget=50000")
    jobs = res.json()
    print(f"Jobs in budget range: {len(jobs)}")
    for j in jobs:
        print(f" - {j['title']} (Budget: {j['budget']})")

    # Test Freelancer Search
    res = requests.get(f"{API_URL}/freelancers/search?skills=Python")
    freelancers = res.json()
    print(f"Freelancers with Python: {len(freelancers)}")
    for f in freelancers:
        print(f" - {f['name']} (Skills: {f['skills']})")

def test_watermark():
    print("\nTesting Watermark Endpoint...")
    # Create a dummy image
    img = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    # Get a contract ID
    c_id = "contract_job_build_an_website_for_my_school_user_fre"
    files = {'file': ('test.jpg', img_byte_arr, 'image/jpeg')}
    res = requests.post(f"{API_URL}/contracts/{c_id}/milestone/0/upload-proof", files=files)
    print(f"Upload Result: {res.status_code} - {res.json()}")
    
    if res.ok:
        filename = res.json()['filename']
        print(f"Proof saved as: {filename}")
        if os.path.exists(f"uploads/proofs/{filename}"):
            print("Verified: Proof file exists on disk.")

if __name__ == "__main__":
    try:
        test_search()
        test_watermark()
    except Exception as e:
        print(f"Verification script failed: {e}")
