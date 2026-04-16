import httpx
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def print_header(title):
    print("\n" + "="*60)
    print(f"🚀 TESTING ENDPOINT: {title}")
    print("="*60)

def print_response(response, explanation):
    print(f"\n💡 WHAT THIS DID: {explanation}")
    if response.status_code == 200:
        data = response.json().get("data", response.json())
        print("\n📥 RESPONSE PREVIEW:")
        print(json.dumps(data, indent=2))
    else:
        print(f"\n❌ ERROR (Status {response.status_code}):")
        print(response.text)
    print("-" * 60)
    time.sleep(3) # Anti-rate-limit buffer

def run_all_tests():
    print("Welcome to the Prompt Optimizer Interactive Test Suite!")
    print("This script will hit every major AI endpoint to show you how the system works.")
    print("Ensure the server is running on port 8000.\n")

    with httpx.Client(timeout=120.0) as client:
        
        # 1. HEALTH CHECK
        print_header("GET /health")
        res = client.get(f"{BASE_URL}/health")
        print_response(res, "Verifies the API is online and responding.")

        # 2. SUGGEST
        print_header("POST /api/suggest")
        res = client.post(f"{BASE_URL}/api/suggest?domain=education&use_case=A math tutor for a 10 year old")
        print_response(res, "Asks Gemini to write a brand new system prompt from scratch based purely on a domain and use-case.")
        
        # Extract the suggested prompt for the next tests
        bad_prompt = "You are a customer support agent. Help the user."
        
        # 3. EVALUATE
        print_header("POST /api/evaluate")
        payload = {"prompt": bad_prompt, "domain": "customer_support"}
        res = client.post(f"{BASE_URL}/api/evaluate", json=payload)
        print_response(res, "Takes our bad prompt ('You are a customer support agent. Help the user.') and rigorously grades it across 7 dimensions (Clarity, Tone, etc).")
        
        # 4. OPTIMIZE
        print_header("POST /api/optimize")
        payload = {
            "prompt": bad_prompt,
            "domain": "customer_support",
            "optimization_goal": "Make it sound incredibly professional and polite"
        }
        res = client.post(f"{BASE_URL}/api/optimize", json=payload)
        print_response(res, "Takes the bad prompt, reads the optimization goal, and rewrites it. Notice the 'improvement' score in the output!")
        
        optimized_prompt = res.json().get("data", {}).get("optimized_prompt", "You are an expert customer support agent...")

        # 5. TEST PROMPT
        print_header("POST /api/test")
        payload = {
            "prompt": optimized_prompt,
            "user_input": "Where is my refund?! It's been 5 days!",
            "domain": "customer_support"
        }
        res = client.post(f"{BASE_URL}/api/test", json=payload)
        print_response(res, "Takes a prompt and a fake angry user message, passes them to Gemini, and then grades Gemini's response on helpfulness, tone, and clarity.")

        # 6. COMPARE (A/B TESTING)
        print_header("POST /api/compare")
        payload = {
            "prompt_a": bad_prompt,
            "prompt_b": optimized_prompt,
            "test_input": "Where is my refund?! It's been 5 days!",
            "domain": "customer_support"
        }
        res = client.post(f"{BASE_URL}/api/compare", json=payload)
        print_response(res, "Pits the Bad Prompt against the Optimized Prompt using the same user query. Gemini acting as a judge decides which prompt resulted in a better answer and why.")

        # 7. VARIANTS
        print_header("POST /api/variants")
        payload = {
            "prompt": "You are a fitness coach.",
            "domain": "healthcare",
            "count": 2,
            "style": "formal"
        }
        res = client.post(f"{BASE_URL}/api/variants", json=payload)
        print_response(res, "Asks the system to write 2 different versions of 'You are a fitness coach.' based on the 'formal' style guideline.")

        # 8. STATS (Dashboard)
        print_header("GET /api/stats")
        res = client.get(f"{BASE_URL}/api/stats")
        print_response(res, "Pulls data from the local SQLite database. Notice how this tracks all the optimizations and tests we just ran!")

        print("\n🎉 ALL TESTS COMPLETE! Check your API terminal history!")

if __name__ == "__main__":
    run_all_tests()
