import os
import stripe
from dotenv import load_dotenv

load_dotenv()

STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")

stripe.api_key = STRIPE_API_KEY

# The ID of the Issuing Card you created (e.g. "ic_1234...")
# This card must be configured for manual approval in test mode.
ISSUING_CARD_ID = os.getenv("ISSUING_CARD_ID")

def simulate_purchase():
    """
    1. Retrieve the ephemeral card details (number, exp, cvc) for the issuing card.
    2. Create a PaymentIntent with that card data in test mode.
    3. Confirm the PaymentIntent to simulate a 'purchase'.
    """

    try:
        # 1. Retrieve ephemeral card details (test mode only)
        card_details = stripe.issuing.CardDetails.create(
            card=ISSUING_CARD_ID
        )
        print("Retrieved ephemeral card details for test mode:")
        print(f"Number: {card_details.number}")
        print(f"Exp: {card_details.exp_month}/{card_details.exp_year}")
        print(f"CVC: {card_details.cvc}")

        # 2. Create a PaymentIntent using that card data
        payment_intent = stripe.PaymentIntent.create(
            amount=1000,  # e.g., $10.00
            currency="usd",
            payment_method_data={
                "type": "card",
                "card": {
                    "number": card_details.number,
                    "exp_month": card_details.exp_month,
                    "exp_year": card_details.exp_year,
                    "cvc": card_details.cvc,
                },
            },
            confirm=True,  # confirm immediately
            description="Test purchase with Issuing card"
        )
        print("PaymentIntent created and confirmed:")
        print(f"ID: {payment_intent.id}, Status: {payment_intent.status}")

    except stripe.error.StripeError as e:
        print("Stripe API error while simulating purchase:", e)
    except Exception as ex:
        print("Unexpected error:", ex)

if __name__ == "__main__":
    simulate_purchase()
