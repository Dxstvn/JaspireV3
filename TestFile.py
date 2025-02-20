import stripe
from flask import Flask, request, jsonify

stripe.api_key = "sk_test_51POM9HCY3Y4d200IE16w7oWDsWvghu1aMNY7ufrrz6tBLAeQQxmbZUQOokgWdfvBAHEDJyN4g4z6kztEBS4RgWFP009rGVfl5C"

app = Flask(__name__)

def test_stripe_issuing_access():
    """
    Quick test to see if your Stripe account has Issuing enabled in test mode.
    """
    try:
        cardholder = stripe.issuing.Cardholder.create(
            type="individual",
            name="Test Issuing Check",
            email="test.issuing@example.com",
            phone_number="+15555555555",
            billing={
                "address": {
                    "line1": "123 Main Street",
                    "city": "San Francisco",
                    "state": "CA",
                    "country": "US",
                    "postal_code": "94111"
                }
            },
            status="active"
        )
        print("Success! Your account appears to have Stripe Issuing in test mode.")
        print(f"Created test cardholder: {cardholder.id}")
    except stripe.error.InvalidRequestError as e:
        print("It seems you don't have Stripe Issuing access (or something else went wrong).")
        print("Error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)

@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    """
    A simple POST-only route for Stripe webhooks.
    Currently returns 200 OK, so Stripe sees it's valid.
    """
    print("Received a webhook request!")
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    # 1. Test your Stripe Issuing access (in test mode)
    test_stripe_issuing_access()

    # 2. Start the Flask server on port 8080
    #    If you do GET on /webhook, you'll get 405 because it's POST-only.
    app.run(port=8080, debug=True)
