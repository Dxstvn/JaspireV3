import os
import stripe
from dotenv import load_dotenv

load_dotenv()

STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
stripe.api_key = STRIPE_API_KEY

def add_funds_for_issuing_test():
    """
    Creates a top-up in test mode to increase your overall Stripe balance.
    Issuing cards draw from this balance.
    """
    try:
        topup = stripe.Topup.create(
            amount=50000,  # e.g. $500.00 (in cents)
            currency="usd",
            description="Add funds for Issuing test",
            statement_descriptor="Issuing test"
        )
        print(f"Top-up created with ID: {topup.id}, status: {topup.status}")

        # In test mode, you can confirm the top-up immediately:
        confirmed_topup = stripe.Topup.confirm(topup.id)
        print(f"After confirm: {confirmed_topup.status}")

        # If status is 'succeeded', your account balance is now increased by amount
    except stripe.error.StripeError as e:
        print("Stripe API error while creating top-up:", e)
    except Exception as ex:
        print("Unexpected error:", ex)

if __name__ == "__main__":
    add_funds_for_issuing_test()
