import requests
from bs4 import BeautifulSoup
import tweepy
import datetime
import os
from dotenv import load_dotenv

load_dotenv()  # Optional: use .env file for keys

# ====================== CONFIG ======================
XAI_API_KEY = os.getenv("XAI_API_KEY")  # Not needed for this simple version

# X/Twitter API Credentials (get from https://developer.x.com)
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
# ===================================================

def get_world_population_data():
    try:
        url = "https://www.worldometers.info/world-population/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Current Population
        pop_tag = soup.find("div", class_="maincounter-number")
        population = int(pop_tag.get_text(strip=True).replace(",", "")) if pop_tag else None
        
        # Daily Growth
        growth = None
        growth_label = soup.find(string=lambda t: t and "Population Growth today" in t)
        if growth_label:
            value_tag = growth_label.find_next("div", class_="maincounter-number") or \
                        growth_label.find_next("span", class_="rts-counter")
            if value_tag:
                growth_text = value_tag.get_text(strip=True).replace(",", "")
                growth = int(growth_text)
        
        return population, growth
    except Exception as e:
        print("Error fetching data:", e)
        return None, None


# ... (keep everything above - the get_world_population_data function)

# === Generate tweet ===
population, daily_growth = get_world_population_data()

if population and daily_growth is not None:
    tweet = f"🌍 World population: {population:,} (+{daily_growth:,} today)"
    
    print("✅ Tweet ready:")
    print(tweet)
    
    # === Send to Make.com Webhook ===
    import requests
    import os
    
    webhook_url = os.getenv("WEBHOOK_URL")
    
    if webhook_url:
        try:
            response = requests.post(
                webhook_url, 
                json={"text": tweet},
                timeout=10
            )
            if response.status_code == 200:
                print("✅ Successfully sent to Make.com → Buffer!")
            else:
                print("❌ Webhook failed:", response.text)
        except Exception as e:
            print("❌ Error sending webhook:", e)
    else:
        print("⚠️ No WEBHOOK_URL found in environment variables")
else:
    print("❌ Failed to get population data")
