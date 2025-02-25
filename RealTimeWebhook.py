import os
from flask import Flask, request, jsonify
import stripe
from dotenv import load_dotenv

load_dotenv()

# Your test secret key
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
# Webhook secret for verifying signatures
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
            # Log merchant data (optional)
            merchant_data = authorization.get("merchant_data", {})
            print(f"Merchant: {merchant_data.get('name')}, MCC: {merchant_data.get('category')}")

            # Approve the authorization using the new TestHelpers endpoint
            try:
                stripe.Issuing.TestHelpers.Authorization.approve(auth_id)
                print(f"Authorization {auth_id} approved via TestHelpers!")
            except stripe.error.StripeError as e_approve:
                print(f"Error approving authorization: {e_approve}")
                return jsonify({'error': 'Authorization approval failed'}), 400

            return jsonify({}), 200

    except stripe.error.SignatureVerificationError as e:
        print(f"Webhook signature verification failed: {e}")
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({'error': 'Webhook processing error'}), 400

    return jsonify({}), 200

if __name__ == "__main__":
    # Listen on all interfaces (0.0.0.0) at port 8080
    app.run(host='0.0.0.0', port=8080)
