import os
import subprocess
import time
from dotenv import load_dotenv

load_dotenv()

# Your test secret key (not needed for CLI, but kept for reference)
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
# The ID of the specific Issuing Card (e.g., "ic_abc123") configured for test mode
ISSUING_CARD_ID = os.getenv("ISSUING_CARD_ID")

def simulate_purchase_with_cli():
    """
    Simulates a purchase by triggering the issuing_authorization.request event using Stripe CLI,
    specifying a particular Issuing card.
    """
    try:
        # Custom merchant data for the simulation
        merchant_data = {
            "category": "eating_places_restaurants",  # MCC for restaurants (5812)
            "name": "Bean Haven Coffee Shop",
            "city": "Seattle",
            "country": "US",
            "postal_code": "98104"
        }
        
        # Format the full event data, including the specific card ID
        event_data = {
            "card": ISSUING_CARD_ID,
            "amount": 1500,  # e.g., $15.00 in cents
            "currency": "usd",
            "merchant_data": merchant_data
        }
        
        # Convert the event data to a JSON string for the CLI command
        event_data_str = (
            f'"card": "{event_data["card"]}", '
            f'"amount": {event_data["amount"]}, '
            f'"currency": "{event_data["currency"]}", '
            f'"merchant_data": {{'
            f'"category": "{merchant_data["category"]}", '
            f'"name": "{merchant_data["name"]}", '
            f'"city": "{merchant_data["city"]}", '
            f'"country": "{merchant_data["country"]}", '
            f'"postal_code": "{merchant_data["postal_code"]}"'
            f'}}'
        )
        
        # Stripe CLI command to trigger the event with custom card and merchant data
        command = ['stripe', 'trigger', 'issuing_authorization.request', '--data', f'{{{event_data_str}}}']
        
        # Run the command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        print("=== Purchase simulation triggered successfully ===")
        print("CLI Output:", result.stdout)
        print(f"Using Issuing Card ID: {ISSUING_CARD_ID}")
        return True
    except subprocess.CalledProcessError as e:
        print("Failed to simulate purchase:", e.stderr)
        return False

if __name__ == "__main__":
    if simulate_purchase_with_cli():
        print("Waiting for webhook to receive the event...")
        time.sleep(3)  # Adjust delay based on your webhook's latency
        print("Simulation complete. Check your webhook logs for the event.")