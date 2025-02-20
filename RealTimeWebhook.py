import os
import stripe
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
STRIPE_SIGNING_SECRET = os.getenv("STRIPE_SIGNING_SECRET")

stripe.api_key = STRIPE_API_KEY

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", None)

    # Verify the webhook signature if we have one
    if STRIPE_SIGNING_SECRET and STRIPE_SIGNING_SECRET.startswith("whsec_"):
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_SIGNING_SECRET
            )
        except stripe.error.SignatureVerificationError:
            print("Invalid signature.")
            return "Invalid signature", 400
        except ValueError:
            print("Invalid payload.")
            return "Invalid payload", 400
    else:
        # If no signing secret, skip verification
        event = None
        try:
            event = stripe.util.json.loads(payload)
        except:
            print("Payload parse error.")
            return "Bad payload", 400

    if event:
        event_type = event.get("type")
        if event_type == "issuing_authorization.request":
            auth_obj = event["data"]["object"]
            merchant_data = auth_obj.get("merchant_data", {})
            mcc = merchant_data.get("category")
            merchant_name = merchant_data.get("name")
            city = merchant_data.get("city")
            country = merchant_data.get("country")

            print("=== issuing_authorization.request ===")
            print(f"MCC: {mcc}")
            print(f"Merchant: {merchant_name}, City: {city}, Country: {country}")

            # Approve transaction
            try:
                stripe.issuing.Authorization.approve(auth_obj["id"])
                print("Transaction approved!")
            except Exception as e:
                print("Error approving authorization:", e)
                return "Error", 400
        else:
            print(f"Received event: {event_type}")

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    # Start the Flask server on port 8080
    # Nginx should proxy https://jaspire.co/webhook -> http://127.0.0.1:8080/webhook
    app.run(port=8080, debug=True)
