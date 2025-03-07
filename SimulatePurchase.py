import os
import subprocess
import stripe
from dotenv import load_dotenv

load_dotenv()

STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
CUSTOMER_ID = os.getenv("CUSTOMER_ID")

stripe.api_key = STRIPE_API_KEY

def get_customer_card():
    try:
        # Retrieve customer's payment methods of type "card"
        payment_methods = stripe.PaymentMethod.list(
            customer=CUSTOMER_ID,
            type="card"
        )
        if not payment_methods.data:
            print("No payment methods found for customer.")
            return None
        # For now, just choose the first available card.
        chosen_card = payment_methods.data[0]
        print(f"Chosen card for simulation: {chosen_card.id}")
        return chosen_card.id
    except Exception as e:
        print("Error retrieving customer payment methods:", str(e))
        return None

def simulate_purchase_with_cli():
    card_id = get_customer_card()
    if not card_id:
        print("Cannot simulate purchase without a valid card.")
        return False

    try:
        # Build the CLI command to trigger the issuing authorization request.
        command = ['stripe', 'trigger', 'issuing_authorization.request']
        # Override the card field with the selected customer payment method card ID.
        command.extend(['--override', f'card={card_id}'])
        print(f"Simulating purchase using card ID: {card_id}")

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        print("=== Purchase simulation triggered successfully ===")
        print("CLI Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("Failed to simulate purchase:", e.stderr)
        return False

if __name__ == "__main__":
    if simulate_purchase_with_cli():
        print("Simulation triggered. Check webhook logs immediately for event handling.")
