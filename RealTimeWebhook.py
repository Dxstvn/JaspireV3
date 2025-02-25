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

    
    # Verify the event signature
    event = stripe.Webhook.construct_event(
        payload, sig_header, STRIPE_SIGNING_SECRET
    )

    if event['type'] == 'issuing_authorization.request':
        authorization = event['data']['object']
        auth_id = authorization["id"]

        print("=== Received Issuing Authorization Request ===")
        # Approve the authorization
    try:
        stripe.issuing.Authorization.modify(
            auth_id,
            status="approved"
        )
        print(f"Authorization {auth_id} approved!")
    except stripe.error.StripeError as e:
        print(f"Error approving authorization: {e}")
        return jsonify({'error': 'Authorization approval failed'}), 400

    # Return a success response within 2 seconds
    return jsonify({}), 200

    #return jsonify({}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)