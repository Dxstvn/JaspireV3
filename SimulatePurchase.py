import os
import subprocess
import time
from dotenv import load_dotenv

load_dotenv()

STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
ISSUING_CARD_ID = os.getenv("ISSUING_CARD_ID")  # For reference only

def simulate_purchase_with_cli():
    """
    Simulates a purchase by triggering the issuing_authorization.request event using Stripe CLI.
    The card is selected by Stripe from active test issuing cards.
    """
    try:
        # Stripe CLI command without --data
        command = ['stripe', 'trigger', 'issuing_authorization.request']
        
        # Execute the command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        print("=== Purchase simulation triggered successfully ===")
        print("CLI Output:", result.stdout)
        if ISSUING_CARD_ID:
            print(f"Note: Intended Issuing Card ID was {ISSUING_CARD_ID}, but Stripe may use a different test card.")
        return True
    except subprocess.CalledProcessError as e:
        print("Failed to simulate purchase:", e.stderr)
        return False

if __name__ == "__main__":
    if simulate_purchase_with_cli():
        print("Waiting for webhook to receive the event...")
        time.sleep(3)  # Adjust based on webhook latency
        print("Simulation complete. Check your webhook logs for the event and card details.")