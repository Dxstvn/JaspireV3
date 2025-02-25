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
            merchant_data = authorization['merchant_data']

            print("=== Received Issuing Authorization Request ===")
            print(f"Merchant Name: {merchant_data['name']}")
            print(f"MCC: {merchant_data['category']}")
            print(f"City: {merchant_data['city']}")
            print(f"Country: {merchant_data['country']}")
            print(f"Postal Code: {merchant_data.get('postal_code', 'N/A')}")

            # Actually approve the authorization via Stripe's Issuing API
            try:
                stripe.issuing.Authorization.approve(authorization["id"])
                print("Transaction approved via the Issuing API!")
            except Exception as approve_error:
                print(f"Error approving authorization: {approve_error}")

            # Return 200 so Stripe knows we've handled the webhook
            return jsonify({}), 200

    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({'error': 'Webhook error'}), 400

    # Return 200 for all other event types
    return jsonify({}), 200

if __name__ == "__main__":
    # Listen on all interfaces (0.0.0.0) at port 8080
    app.run(host='0.0.0.0', port=8080)
