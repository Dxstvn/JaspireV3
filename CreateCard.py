import os
import stripe
from dotenv import load_dotenv

load_dotenv()

STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")

# The ID of the existing cardholder (e.g. "ich_1234...") that you created previously
EXISTING_CARDHOLDER_ID = os.getenv("STRIPE_CARDHOLDER_ID")

stripe.api_key = STRIPE_API_KEY

def create_card_for_existing_cardholder():
    """
    Creates a new virtual card for an existing cardholder, 
    configured for real-time (manual) authorization so 
    'issuing_authorization.request' events fire.
    """
    try:
        card = stripe.issuing.Card.create(
            cardholder=EXISTING_CARDHOLDER_ID,
            currency="usd",
            type="virtual",
            spending_controls={
                # By default, if you set no auto-approval categories, 
                # transactions should trigger 'issuing_authorization.request'
                "allowed_categories": [],
                "blocked_categories": [],
            },
            status="active"
        )
        print(f"Created new card for cardholder {EXISTING_CARDHOLDER_ID}")
        print(f"Card ID: {card.id}, Last4: {card.last4}")
        return card
    except stripe.error.StripeError as e:
        print("Error creating card:", e)
    except Exception as ex:
        print("Unexpected error:", ex)

if __name__ == "__main__":
    new_card = create_card_for_existing_cardholder()
