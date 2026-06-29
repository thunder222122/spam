import asyncio
import aiohttp
import os
import random
import time

# ========== CONFIGURATION ==========
# Token from environment variable (set before running)
# Windows: set DISCORD_TOKEN=your_token_here
# Linux/Mac: export DISCORD_TOKEN=your_token_here
TOKEN = os.getenv("TOKEN")

# Channel ID to send messages to
CHANNEL_ID = 1521105893272584252  # Replace with your channel ID

# Message to spam
MESSAGE = "# <@1517509201163849779> shut the fuck up bitch ass nigga ur shitty as fuck and ur fucking lame cuck ass nigga my client stays online until the earth gets annihilated lets fucking see how long you last nigga im the fucking lord in cleinting no one in this fucking com can win from my in client outlast faggot ass nigga im gonna obliterate ur fucking tokens"

# Delay between messages (in seconds)
DELAY = 2.0  # Adjust as needed

# Number of messages to send (None = infinite)
MAX_MESSAGES = None  # Set to a number like 50 to stop after that many

# Proxy support (optional)
PROXY = None  # Set to "http://user:pass@host:port" if needed

# ========== SPAM LOGIC ==========

async def send_messages(session: aiohttp.ClientSession, token: str, 
                         channel_id: int, message: str, delay: float, 
                         max_msgs: int, proxy: str = None):
    """Send messages with specified delay"""
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    
    sent = 0
    while max_msgs is None or sent < max_msgs:
        try:
            async with session.post(url, json={"content": message}, headers=headers, proxy=proxy) as resp:
                if resp.status in (200, 204):
                    sent += 1
                    print(f"[{time.strftime('%H:%M:%S')}] Sent message #{sent}")
                elif resp.status == 429:
                    # Rate limited - wait and retry
                    retry_after = (await resp.json()).get('retry_after', 5)
                    print(f"[{time.strftime('%H:%M:%S')}] Rate limited, waiting {retry_after}s")
                    await asyncio.sleep(retry_after)
                    continue
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] Failed: HTTP {resp.status}")
                    if resp.status == 401:
                        print("Token invalid! Check your DISCORD_TOKEN.")
                        break
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Error: {e}")
        
        await asyncio.sleep(delay)
    
    print(f"[{time.strftime('%H:%M:%S')}] Finished (sent {sent} messages)")

async def main():
    if not TOKEN:
        print(" No token found!")
        print("Set DISCORD_TOKEN environment variable:")
        print("  Windows: set DISCORD_TOKEN=your_token_here")
        print("  Linux/Mac: export DISCORD_TOKEN=your_token_here")
        return
    
    print(f"Starting spam with 1 token...")
    print(f"Channel: {CHANNEL_ID}")
    print(f"Message: {MESSAGE[:50]}...")
    print(f"Delay: {DELAY}s per message")
    if MAX_MESSAGES:
        print(f"Max messages: {MAX_MESSAGES}")
    else:
        print("Infinite mode (press Ctrl+C to stop)")
    
    # Optional warm-up
    warmup = 60  # 1 minute
    print(f"\n Waiting {warmup}s before starting to avoid detection...")
    for i in range(warmup, 0, -10):
        print(f"   {i}s remaining...")
        await asyncio.sleep(10)
    print(" Warm-up complete! Starting now...\n")
    
    async with aiohttp.ClientSession() as session:
        try:
            await send_messages(session, TOKEN, CHANNEL_ID, MESSAGE, DELAY, MAX_MESSAGES, PROXY)
        except KeyboardInterrupt:
            print("\n Stopped by user.")

if __name__ == "__main__":
    asyncio.run(main())
