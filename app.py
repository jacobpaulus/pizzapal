from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Restrict allowed origins to your production domain.
CORS(app, resources={
    r"/*": {
        "origins": ["https://www.popuppizza.co", "http://127.0.0.1:5001", "http://localhost:5001"],
        "allow_headers": ["Content-Type", "Authorization", "User-Agent", "Accept", "Origin"],
        "methods": ["GET", "POST", "OPTIONS"]
    }
})

allowed_origin = ["https://www.popuppizza.co", "http://127.0.0.1:5001", "http://localhost:5001"]

@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        return '', 200


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = ", ".join(allowed_origin)
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

@app.route('/start_chat', methods=['GET'])
def start_chat():
    response = {
        "reply": "Hello, I'm PizzaPal! How can I help you today?",
        "buttons": [
            {"label": "FAQs", "value": "faqs"},
            {"label": "Events", "value": "events"},
            {"label": "Something Else", "value": "something_else"}
        ]
    }
    return jsonify(response)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(force=True)
        print("\n📢 [Flask] Received Chat Request:", data)
    except Exception as e:
        return jsonify({"reply": f"❌ ERROR: Could not parse JSON - {str(e)}"}), 400

    if not data or "message" not in data:
        return jsonify({"reply": "❌ ERROR: No 'message' key in received data"}), 400

    user_message = data.get("message", "").strip().lower()
    print(f"📢 [Flask] Processed user_message: '{user_message}'")

    faq_categories = {
        "General Questions": {
            "What types of events does PUPC cater for?": "We specialise in catering for weddings, private parties, corporate events, festivals, and local pop-ups.",
            "What areas do we cover?": "We serve Gloucestershire, Worcestershire, Bristol, Oxfordshire, and the Cotswolds.",
            "How far in advance should you book?": "We recommend booking as soon as you have a date in mind, especially for peak seasons.",
            "Do we offer vegetarian, vegan, or gluten-free options?": "Absolutely! We have vegetarian, vegan, and gluten-free pizza options available.",
            "What size are your pizzas, and how many do you serve per event?": (
                "Our pizzas are 12-inch, hand-stretched Neapolitan-style, cooked fresh in our wood-fired oven. "
                "We serve whatever quantity is requested. Don’t worry, if you are slightly unsure about numbers, "
                "we are always happy to bring a few extra pizzas which can be offered as takeaway options if spare."
            )
        },
        "Booking and Pricing": {
            "How much does it cost to hire PUPC?": "Pricing depends on guest count, menu selection, and location. Packages start from £300.",
            "Do you require a deposit?": "Yes, we usually ask for a 20% deposit to secure the date.",
            "Is there a minimum or maximum number of guests?": "Our minimum booking is 20 guests, and we can cater for up to 300 guests.",
            "What happens if I need to cancel or reschedule?": "Deposits are non-refundable, but we’ll work with you to reschedule if needed."
        },
        "The Event": {
            "How long do you need to set up?": "We typically arrive 60-90 minutes before serving time to set up.",
            "How long do you serve for?": "We generally serve for 2-3 hours, but this can be adjusted based on your event.",
            "What does PUPC require from you?": "A flat surface of at least 3m x 3m. We are fully self-sufficient. We need no electricity or gas.",
            "What style is our catering service?": "We can do buffet-style service, individual servings, or a mix."
        },
        "Food": {
            "What pizzas do PUPC offer?": "We offer all the authentic classics, as well as rotating specials.",
            "Is our pizza wood-fired?": "Yes! Our oven reaches over 600°C, allowing us to serve over 60 pizzas an hour.",
            "Do we use fresh ingredients?": "Yes! We use 100% fresh, locally sourced ingredients."
        },
        "Special Requests": {
            "Can I customize my pizza?": "Absolutely! Let’s chat about ideas.",
            "Do we provide side dishes or desserts?": "Yes, we offer garlic bread and sweet treats upon request.",
            "Can we add drinks or other services?": "Yes, let us know in advance, and we can cater to your needs."
        },
        "Hygiene": {
            "Do you have food hygiene certification?": "Yes, we are fully insured and have a 5-star food hygiene rating."
        }
    }

    if user_message == "faqs":
        response = {"reply": "Please choose a category:", "options": list(faq_categories.keys())}
    elif user_message in faq_categories:
        response = {"reply": f"Here are some {user_message} FAQs:", "options": list(faq_categories[user_message].keys())}
    elif any(user_message in faq_dict for faq_dict in faq_categories.values()):
        for category, faq_dict in faq_categories.items():
            if user_message in faq_dict:
                response = {"reply": faq_dict[user_message]}
                break
    elif user_message == "events":
        response = {"reply": "Tell me about your event! How many guests will be attending?"}
    elif user_message == "something_else":
        response = {"reply": "Sure! Please type your question and I'll do my best to help."}
    else:
        response = {"reply": f"🤖 I received: '{user_message}', but I don't recognize it. Please try again."}

    print("\n📢 [Flask] Sending Chat Response:", response)
    return jsonify(response)

@app.route('/submit_event', methods=['POST'])
def submit_event():
    try:
        data = request.get_json(force=True)
        print("\n📢 [Flask] Received Event Enquiry Submission:", data)
    except Exception as e:
        return jsonify({"reply": f"❌ ERROR: Could not parse JSON - {str(e)}"}), 400

    required_fields = [
        'name', 'event_type', 'event_date', 'event_time', 'event_location',
        'number_of_guests', 'catering_budget', 'contact_email', 'contact_number',
        'special_requests'
    ]
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    if missing_fields:
        return jsonify({"reply": f"Missing fields: {', '.join(missing_fields)}"}), 400

    email_content = (
        f"New event enquiry from PizzaPal:\n\n"
        f"Name: {data.get('name')}\n"
        f"Event Type: {data.get('event_type')}\n"
        f"When: {data.get('event_date')}\n"
        f"Time: {data.get('event_time')}\n"
        f"Location: {data.get('event_location')}\n"
        f"Number of Guests: {data.get('number_of_guests')}\n"
        f"Catering Budget: {data.get('catering_budget')}\n"
        f"Contact Email: {data.get('contact_email')}\n"
        f"Contact Number: {data.get('contact_number')}\n"
        f"Special Requests/Details: {data.get('special_requests')}\n"
    )

    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    receiver_email = "popuppizzaco@gmail.com"
    subject = "New PizzaPal Event Enquiry"

    msg = MIMEText(email_content)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.login(sender_email, sender_password)
        smtp_server.sendmail(sender_email, receiver_email, msg.as_string())
        smtp_server.quit()
        return jsonify({"reply": "Thank you for your submission, one of our team will be in touch shortly to discuss your event."})
    except Exception as e:
        print("📢 [Flask] Email sending failed:", e)
        return jsonify({"reply": "There was an error submitting your enquiry. Please try again later."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)


