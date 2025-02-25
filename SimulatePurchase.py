import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
ISSUING_CARD_ID = os.getenv("ISSUING_CARD_ID")

def simulate_purchase_with_cli():
    try:
        command = ['stripe', 'trigger', 'issuing_authorization.request']
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        print("=== Purchase simulation triggered successfully ===")
        print("CLI Output:", result.stdout)
        if ISSUING_CARD_ID:
            print(f"Note: Intended Card ID: {ISSUING_CARD_ID}. Check webhook logs for actual card used.")
        return True
    except subprocess.CalledProcessError as e:
        print("Failed to simulate purchase:", e.stderr)
        return False

if __name__ == "__main__":
    if simulate_purchase_with_cli():
        print("Simulation triggered. Check webhook logs immediately for event handling.")