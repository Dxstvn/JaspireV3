import os
from flask import Flask, request, jsonify
import stripe
from dotenv import load_dotenv

load_dotenv()

STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
STRIPE_SIGNING_SECRET = os.getenv("STRIPE_SIGNING_SECRET")

stripe.api_key = STRIPE_API_KEY

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')

    try:
        # Verify the event signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_SIGNING_SECRET
        )

        if event['type'] == 'issuing_authorization.request':
            authorization = event['data']['object']
            auth_id = authorization["id"]

            print("=== Received Issuing Authorization Request ===")
            # 1) Safely get cardholder ID (handles string or object)
            cardholder = authorization.get("cardholder", {})
            if isinstance(cardholder, str):
                cardholder_id = cardholder
            elif isinstance(cardholder, dict) and "id" in cardholder:
                cardholder_id = cardholder["id"]
            else:
                print("Error: Could not determine cardholder ID")
                return jsonify({'error': 'Invalid cardholder data'}), 400

            # 2) Approve authorization immediately to meet 2-second deadline
            try:
                stripe.issuing.Authorization.approve(auth_id)
                print(f"Authorization {auth_id} approved!")
            except stripe.error.StripeError as e:
                print(f"Error approving authorization: {e}")
                return jsonify({'error': 'Authorization approval failed'}), 400

            # 3) Asynchronously check and update cardholder (outside critical path)
            try:
                ch = stripe.issuing.Cardholder.retrieve(cardholder_id)
                requirements_info = ch.get("requirements", {})
                disabled_reason = requirements_info.get("disabled_reason")

                if disabled_reason:
                    print(f"Cardholder {cardholder_id} has issues: {disabled_reason}")
                    stripe.issuing.Cardholder.update(
                        cardholder_id,
                        individual={
                            "first_name": "Test",
                            "last_name": "User",
                            "dob": {"day": 1, "month": 1, "year": 2000},
                            "id_number": "000000000"
                        },
                        billing={
                            "address": {
                                "line1": "123 RealTime Street",
                                "city": "San Francisco",
                                "state": "CA",
                                "country": "US",
                                "postal_code": "94111"
                            }
                        },
                        status="active"
                    )
                    print(f"Updated cardholder {cardholder_id} post-approval.")
            except stripe.error.StripeError as e:
                print(f"Background cardholder update failed: {e}")

            return jsonify({}), 200

    except stripe.error.SignatureVerificationError as e:
        print(f"Webhook signature verification failed: {e}")
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({'error': 'Webhook processing error'}), 400

    return jsonify({}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)