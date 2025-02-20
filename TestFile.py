import stripe
from flask import Flask, request, jsonify

stripe.api_key = "sk_test_51POM9HCY3Y4d200IE16w7oWDsWvghu1aMNY7ufrrz6tBLAeQQxmbZUQOokgWdfvBAHEDJyN4g4z6kztEBS4RgWFP009rGVfl5C"

# def create_test_payment_intent():
#     intent = stripe.PaymentIntent.create(
#         amount=1000,           # amount in cents (e.g., $10.00)
#         currency='usd',
#         payment_method_types=['card'],
#     )
#     return intent

# if __name__ == "__main__":
#     payment_intent = create_test_payment_intent()
#     print("Created PaymentIntent:", payment_intent.id)

def test_stripe_issuing_access():
    try:
        # Attempt to create a Cardholder in test mode
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
        # This usually indicates you don't have Issuing access or the endpoint is not available
        print("It seems you don't have Stripe Issuing access (or something else went wrong).")
        print("Error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)

if __name__ == "__main__":
    test_stripe_issuing_access()