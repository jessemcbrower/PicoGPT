#!/usr/bin/env python3
# test_api.py
# Test script to debug OpenAI API calls locally on Mac

import json
import requests

# API Configuration
OPENAI_API_KEY = "YOUR_API_KEY_HERE"  # Replace with your OpenAI API key

HEADERS = {
    "Authorization": "Bearer " + OPENAI_API_KEY,
    "Content-Type": "application/json",
}

SYSTEM_INSTRUCTION = (
    "You are a helpful assistant running on a tiny calculator. "
    "Keep answers short (1–3 sentences) and avoid long lists."
)


def test_chat_completions(user_text, model="gpt-4o-mini"):
    """Test standard /v1/chat/completions endpoint"""
    url = "https://api.openai.com/v1/chat/completions"
    
    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "user", "content": user_text}
    ]
    
    payload = {
        "model": model,
        "messages": messages
    }
    
    print("=" * 60)
    print("TEST: /v1/chat/completions endpoint")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Model: {model}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload)
        print(f"Status Code: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            reply = data["choices"][0]["message"]["content"]
            print("✅ SUCCESS!")
            print(f"Reply: {reply}")
            return True, reply, url, model, "messages"
        else:
            print(f"❌ FAILED: {resp.text}")
            return False, None, url, model, "messages"
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, None, url, model, "messages"


def test_responses_endpoint(user_text, model="gpt-4o-mini"):
    """Test /v1/responses endpoint (if it exists)"""
    url = "https://api.openai.com/v1/responses"
    
    full_prompt = f"System: {SYSTEM_INSTRUCTION}\n\nNew question:\nUser: {user_text}"
    
    payload = {
        "model": model,
        "input": full_prompt
    }
    
    print("=" * 60)
    print("TEST: /v1/responses endpoint")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Model: {model}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload)
        print(f"Status Code: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            # Try to extract reply based on expected structure
            if "output" in data:
                reply = data["output"][0]["content"][0]["text"]
            else:
                reply = str(data)  # Fallback
            print("✅ SUCCESS!")
            print(f"Reply: {reply}")
            return True, reply, url, model, "input"
        else:
            print(f"❌ FAILED: {resp.text}")
            return False, None, url, model, "input"
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, None, url, model, "input"


if __name__ == "__main__":
    print("Testing OpenAI API calls...")
    print()
    
    test_question = "Hello, how are you?"
    print(f"Test Question: {test_question}")
    print()
    
    # Test standard chat endpoint first (most likely to work)
    success1, reply1, url1, model1, format1 = test_chat_completions(test_question)
    print()
    
    if success1:
        print("=" * 60)
        print("✅ WORKING CONFIGURATION FOUND!")
        print("=" * 60)
        print(f"Endpoint: {url1}")
        print(f"Model: {model1}")
        print(f"Format: {format1}")
        print(f"Reply: {reply1}")
        print()
        print("This configuration will be used in PicoGPT.py")
    else:
        # Try responses endpoint
        print()
        success2, reply2, url2, model2, format2 = test_responses_endpoint(test_question)
        print()
        
        if success2:
            print("=" * 60)
            print("✅ WORKING CONFIGURATION FOUND!")
            print("=" * 60)
            print(f"Endpoint: {url2}")
            print(f"Model: {model2}")
            print(f"Format: {format2}")
            print(f"Reply: {reply2}")
            print()
            print("This configuration will be used in PicoGPT.py")
        else:
            print("=" * 60)
            print("❌ BOTH ENDPOINTS FAILED")
            print("=" * 60)
            print("Troubleshooting:")
            print("1. Check if API key is valid")
            print("2. Check if you have quota/credits")
            print("3. Check your OpenAI account status")
