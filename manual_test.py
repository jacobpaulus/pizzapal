import requests
import json

BASE_URL = "https://www.popuppizza.co"  # Your production domain
CHAT_URL = f"{BASE_URL}/chat"
EVENT_URL = f"{BASE_URL}/submit_event"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",
    "Origin": "https://www.popuppizza.co"  # Must match the allowed origins in Flask CORS settings
}

def test_faqs():
    """Test FAQs endpoint"""
    data = {"message": "faqs"}
    print("\n🟢 Step 1: Sending 'faqs' to /chat")
    response = requests.post(CHAT_URL, json=data, headers=HEADERS)
    print("Response status code:", response.status_code)
    try:
        faq_response = response.json()
        print("✅ Full JSON Response from /chat:")
        print(json.dumps(faq_response, indent=2))
    except json.JSONDecodeError:
        print("❌ ERROR: Could not parse JSON from /chat.")

def test_event_submission():
    """Test Event Submission endpoint"""
    event_data = {
        "name": "John Doe",
        "event_type": "Wedding",
        "event_date": "2025-08-12",
        "event_time": "6:00 PM",
        "event_location": "Gloucester",
        "number_of_guests": "100",
        "catering_budget": "£2000",
        "contact_email": "johndoe@email.com",
        "contact_number": "07123456789",
        "special_requests": "Vegan options required"
    }
    print("\n🟢 Step 2: Submitting Event Enquiry to /submit_event")
    response = requests.post(EVENT_URL, json=event_data, headers=HEADERS)
    print("Response status code:", response.status_code)
    try:
        event_response = response.json()
        print("✅ Full JSON Response from /submit_event:")
        print(json.dumps(event_response, indent=2))
    except json.JSONDecodeError:
        print("❌ ERROR: Could not parse JSON from /submit_event.")

if __name__ == "__main__":
    test_faqs()
    test_event_submission()

