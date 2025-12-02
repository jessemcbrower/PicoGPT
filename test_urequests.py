#!/usr/bin/env python3
# test_urequests.py
# Test script that simulates urequests behavior

import json
import requests

# Simulate urequests - it doesn't have json= parameter
def urequests_post(url, headers=None, data=None):
    """Simulate urequests.post() - uses data= not json="""
    if isinstance(data, str):
        # Already a string
        return requests.post(url, headers=headers, data=data)
    else:
        # Convert to JSON string
        return requests.post(url, headers=headers, data=json.dumps(data))

# API Configuration
OPENAI_API_KEY = "YOUR_API_KEY_HERE"  # Replace with your OpenAI API key
OPENAI_MODEL = "gpt-4o-mini"
API_URL = "https://api.openai.com/v1/chat/completions"

HEADERS = {
    "Authorization": "Bearer " + OPENAI_API_KEY,
    "Content-Type": "application/json",
}

SYSTEM_INSTRUCTION = (
    "You are a helpful assistant running on a tiny calculator. "
    "Keep answers short (1–3 sentences) and avoid long lists."
)

# Test the exact same code as PicoGPT.py
def ask_model(user_text, history=None):
    """Exact copy of ask_model from PicoGPT.py"""
    # Build messages array (standard format)
    messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
    
    # Add recent conversation history if provided
    if history and isinstance(history, list) and len(history) > 0:
        recent = history[-6:] if len(history) > 6 else history
        messages.extend(recent)
    
    # Add current user message
    messages.append({"role": "user", "content": user_text})
    
    # Construct payload (standard chat/completions format)
    payload = {
        "model": OPENAI_MODEL,
        "messages": messages
    }
    
    print("=" * 60)
    print("TESTING EXACT PicoGPT.py CODE")
    print("=" * 60)
    print(f"URL: {API_URL}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    # Send POST request (using urequests simulation)
    resp = None
    try:
        # This is how PicoGPT.py does it now
        resp = urequests_post(API_URL, headers=HEADERS, data=payload)
        
        print(f"Status Code: {resp.status_code}")
        print(f"Response Headers: {dict(resp.headers)}")
        print()
        
        # Check status code
        if resp.status_code != 200:
            error_text = resp.text if hasattr(resp, 'text') else str(resp.status_code)
            print(f"ERROR: {error_text}")
            raise RuntimeError("HTTP {}: {}".format(resp.status_code, error_text))
        
        # Parse JSON response
        data = resp.json()
        print("Response JSON:")
        print(json.dumps(data, indent=2))
        print()
        
        # Extract answer text (standard chat/completions format)
        if "choices" in data and len(data["choices"]) > 0:
            reply = data["choices"][0]["message"]["content"]
            print("✅ SUCCESS!")
            print(f"Reply: {reply}")
            return reply
        else:
            raise RuntimeError("No 'choices' field in response")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        # Always close the response
        if resp is not None:
            resp.close()

if __name__ == "__main__":
    print("Testing with urequests simulation...")
    print()
    
    try:
        reply = ask_model("Hello, how are you?")
        print()
        print("=" * 60)
        print("✅ CODE WORKS! This is what PicoGPT.py will do.")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ CODE FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        print("This error will also happen on the device.")

