import os
from flask import Flask, request, jsonify
import stripe
from dotenv import load_dotenv
import json
from django.http import HttpResponse

load_dotenv()

STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
STRIPE_SIGNING_SECRET = os.getenv("STRIPE_SIGNING_SECRET")

stripe.api_key = STRIPE_API_KEY

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    request_data = json.loads(request.data)
    signature = request.headers.get('Stripe-Signature')
    
    # Verify webhook signature and extract the event.
    try:
        event = stripe.Webhook.construct_event(
            payload=request.data,
            sig_header=signature,
            secret=STRIPE_SIGNING_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event["type"] == "issuing_authorization.request":
        auth = event["data"]["object"]

        print("=== Received Issuing Authorization Request ===")
        merchant_data = auth.get("merchant_data", {})
        print(f"Merchant Name: {merchant_data.get('name')}")
        print(f"MCC: {merchant_data.get('category')}")
        print(f"City: {merchant_data.get('city')}")
        print(f"Country: {merchant_data.get('country')}")
        print(f"Postal Code: {merchant_data.get('postal_code', 'N/A')}")
        
        # Log the card ID used in the simulated authorization.
        card_id_used = auth.get("card")
        print(f"Card used in authorization: {card_id_used}")

    # Return a success response.
    return json.dumps({"approved": True}), 200, {
        "Stripe-Version": "2022-08-01",
        "Content-Type": "application/json"
    }

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
