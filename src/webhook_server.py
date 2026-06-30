import os
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONEncoder
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Digital Product System Webhook Server")

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
BEEHIIV_API_KEY = os.getenv("BEEHIIV_API_KEY")
BEEHIIV_PUBLICATION_ID = os.getenv("BEEHIIV_PUBLICATION_ID")

def send_discord_notification(product_name, price, email):
    if not DISCORD_WEBHOOK_URL:
        print("[Simulation Webhook] Missing DISCORD_WEBHOOK_URL. Simulated Discord notification:")
        print(f" Sale notification: {product_name} sold for ${price} to {email}")
        return
        
    # Send a Discord embed notification
    payload = {
        "embeds": [
            {
                "title": "🎉 New Sale Recorded!",
                "color": 3066993,  # Green
                "fields": [
                    {"name": "Product", "value": product_name, "inline": True},
                    {"name": "Price", "value": f"${price}", "inline": True},
                    {"name": "Customer", "value": email, "inline": False}
                ],
                "footer": {"text": "Digital Product Autopilot System"}
            }
        ]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        print("Discord notification sent successfully.")
    except Exception as e:
        print(f"Error sending Discord notification: {e}")

def tag_beehiiv_subscriber(email, product_name):
    if not BEEHIIV_API_KEY or not BEEHIIV_PUBLICATION_ID:
        print("[Simulation Webhook] Missing Beehiiv API key. Simulated tagging:")
        print(f" Tagging subscriber {email} with: customer_{product_name}")
        return
        
    url = f"https://api.beehiiv.com/v2/publications/{BEEHIIV_PUBLICATION_ID}/subscribers"
    headers = {
        "Authorization": f"Bearer {BEEHIIV_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # We first register/find the subscriber to apply the tag
    data = {
        "email": email,
        "custom_fields": [
            {"name": "customer_status", "value": "paid"},
            {"name": "purchased_product", "value": product_name}
        ]
    }
    
    try:
        # Upsert subscriber with custom purchase tags
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"Tagged subscriber {email} in Beehiiv.")
    except Exception as e:
        print(f"Error tagging subscriber in Beehiiv: {e}")

@app.post("/webhooks/gumroad")
async def gumroad_webhook(request: Request):
    payload = await request.form()
    # Gumroad sends form-urlencoded data by default
    data = dict(payload)
    
    # If JSON instead
    if not data:
        try:
            data = await request.json()
        except:
            pass
            
    if not data:
        raise HTTPException(status_code=400, detail="Invalid request body")
        
    print(f"Received Gumroad Webhook: {data}")
    
    email = data.get("email")
    product_name = data.get("product_name", "Unknown Product")
    price = data.get("price", "0.00")
    
    # Standardize price division if sent in cents
    if price.isdigit() and len(price) > 2:
        price = f"{float(price)/100:.2f}"
        
    if email:
        # 1. Notify Discord
        send_discord_notification(product_name, price, email)
        # 2. Tag in Beehiiv
        tag_beehiiv_subscriber(email, product_name)
        
    return {"status": "success", "processed": True}

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    try:
        data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
    print(f"Received Stripe Webhook Event: {data.get('type')}")
    
    # Check for checkout session completed
    if data.get("type") == "checkout.session.completed":
        session = data.get("data", {}).get("object", {})
        email = session.get("customer_details", {}).get("email")
        amount_total = session.get("amount_total", 0) / 100
        price = f"{amount_total:.2f}"
        
        # Pull products purchased
        product_name = "Digital Product Purchase"
        
        if email:
            send_discord_notification(product_name, price, email)
            tag_beehiiv_subscriber(email, product_name)
            
    return {"status": "success", "processed": True}

def run_server(port=8000):
    import uvicorn
    print(f"Starting FastAPI Webhook Server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
