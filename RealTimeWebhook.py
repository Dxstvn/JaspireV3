import os
from flask import Flask, request, jsonify
import stripe
from stripe import api_requestor
from dotenv import load_dotenv

load_dotenv()

STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
STRIPE_SIGNING_SECRET = os.getenv("STRIPE_SIGNING_SECRET")

stripe.api_key = STRIPE_API_KEY

app = Flask(__name__)

def approve_authorization_in_test_mode(authorization_id):
    """
    Directly calls the test_helpers endpoint:
      POST /v1/test_helpers/issuing/authorizations/{authorization_id}/approve
    using Stripe's low-level request machinery.
    """
    # Create a requestor bound to your API key
    requestor = stripe.api_requestor.APIRequestor(api_key=stripe.api_key)
    url = f"/v1/test_helpers/issuing/authorizations/{authorization_id}/approve"

    # Perform a POST request to that endpoint
    response, _ = requestor.request("post", url)
    return response

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

            # Retrieve the cardholder from the authorization
            cardholder_info = authorization.get("cardholder", {})
            if isinstance(cardholder_info, dict):
                cardholder_id = cardholder_info.get("id")
            else:
                cardholder_id = cardholder_info  # fallback if it's a string

            # 1) Fix the cardholder if disabled due to missing test KYC
            try:
                ch = stripe.issuing.Cardholder.retrieve(cardholder_id)
                disabled_reason = ch.get("requirements", {}).get("disabled_reason")
                if disabled_reason:
                    print(f"Cardholder {cardholder_id} unverified: {disabled_reason}")
                    # Provide minimal test data
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
                    print(f"Updated cardholder {cardholder_id} for test KYC.")
            except Exception as ch_update_error:
                print(f"Error updating cardholder for verification: {ch_update_error}")

            # 2) Approve the authorization in test mode
            try:
                resp = approve_authorization_in_test_mode(auth_id)
                print(f"Approved auth {auth_id} in test mode! Response: {resp}")
            except Exception as approve_error:
                print(f"Error approving authorization: {approve_error}")
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
    app.run(host='0.0.0.0', port=8080)
