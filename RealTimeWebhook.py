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

            print("=== Received Issuing Authorization Request ===")
            # 1) Retrieve the cardholder from the authorization
            cardholder_id = authorization["cardholder"]["id"]
            ch = stripe.issuing.Cardholder.retrieve(cardholder_id)

            # 2) Check if cardholder is disabled or pending verification
            #    e.g. ch["requirements"]["disabled_reason"] might be "verification_required"
            #    We'll forcibly update the cardholder with minimal test data
            requirements_info = ch.get("requirements", {})
            disabled_reason = requirements_info.get("disabled_reason")

            if disabled_reason:
                print(f"Cardholder {cardholder_id} has outstanding requirements: {disabled_reason}")
                try:
                    # Update the cardholder with minimal test KYC data
                    # Adjust fields as needed for your region
                    updated_ch = stripe.issuing.Cardholder.update(
                        cardholder_id,
                        individual={
                            "first_name": "Test",
                            "last_name": "User",
                            "dob": {"day": 1, "month": 1, "year": 2000},
                            "id_number": "000000000"  # Some test ID
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
                        status="active"  # Ensure the cardholder is active
                    )
                    print(f"Updated cardholder {cardholder_id} to fulfill test KYC requirements.")
                except Exception as e_update:
                    print(f"Error updating cardholder for verification: {e_update}")

            # 3) Finally, approve the authorization
            try:
                stripe.issuing.Authorization.approve(authorization["id"])
                print(f"Authorization {authorization['id']} approved!")
            except Exception as e_approve:
                print(f"Error approving authorization: {e_approve}")

            return jsonify({}), 200

    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({'error': 'Webhook error'}), 400

    return jsonify({}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
