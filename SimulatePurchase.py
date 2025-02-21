import os
import stripe
from dotenv import load_dotenv

load_dotenv()

# Your test secret key
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
# The ID of an Issuing Card (e.g., "ic_abc123") configured for test mode
ISSUING_CARD_ID = os.getenv("ISSUING_CARD_ID")

stripe.api_key = STRIPE_API_KEY

def create_test_authorization():
    """
    Creates a test-mode Issuing Authorization via Stripe's test_helpers endpoint.
    This simulates a purchase on your Issuing card in test mode.
    """
    try:
        # Using the new test_helpers API for issuing authorizations
        authorization = stripe.Issuing.TestHelpers.Authorization.create(
            card=ISSUING_CARD_ID,
            amount=1500,  # e.g., $15.00 in cents
            currency="usd",
            merchant_data={
                # Merchant Category Code (e.g., 5732 = "Variety Store"), see docs
                "category": "5732",
                "name": "Example Merchant",
                "city": "San Francisco",
                "country": "US"
            }
            # You can add more fields like 'pending_request', etc. if desired
        )
        print("=== Created test-mode authorization ===")
        print(f"ID: {authorization.id}")
        print(f"Status: {authorization.status}")
        print(f"MCC: {authorization.merchant_data.category}")
        print(f"Merchant Name: {authorization.merchant_data.name}")
        return authorization

    except stripe.error.StripeError as e:
        print("Error creating test authorization:", e)
    except Exception as ex:
        print("Unexpected error:", ex)

if __name__ == "__main__":
    create_test_authorization()
