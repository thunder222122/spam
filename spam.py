import asyncio
import aiohttp
import random
import time

# ========== CONFIGURATION ==========
# List of Discord tokens (user tokens)
TOKENS = [
    "MTUwMjk5NTI1MzgwMjU2NTYzMg.GHrxTe.X4rItmK_3l6eRyJ70J2hBuFeOPWwKsz6l1KUbs",
    "MTUwNTE4NDkwNzQzMTkwMzI4Mg.Goi5gt.1O3xKzWnxMFXkP7giiE-V9TFEX289HfdPx8O6Q,
    # Add as many as you want
]

# Channel ID to send messages to
CHANNEL_ID = 1521105893272584252  # Replace with your channel ID

# Message to spam
MESSAGE = "# <@1517509201163849779> shut the fuck up bitch ass nigga ur shitty as fuck and ur fucking lame cuck ass nigga my client stays online until the earth gets annihilated lets fucking see how long you last nigga im the fucking lord in cleinting no one in this fucking com can win from my in client outlast faggot ass nigga im gonna obliterate ur fucking tokens  "

# Delay between messages per token (in seconds)
DELAY = 2.0  # Adjust as needed

# Number of messages to send per token (None = infinite)
MAX_MESSAGES = None  # Set to a number like 50 to stop after that many per token

# Proxy support (optional) - list of proxies in format "http://user:pass@host:port"
PROXIES = [
    # "http://user:pass@proxy1:8080",
    # "http://user:pass@proxy2:8080",
]  # Leave empty to use direct connection

# ========== SPAM LOGIC ==========

async def send_messages(session: aiohttp.ClientSession, token: str, alias: str, 
                         channel_id: int, message: str, delay: float, 
                         max_msgs: int, proxy: str = None):
    """Send messages from a single token with specified delay"""
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
                    print(f"[{alias}] Sent message #{sent}")
                elif resp.status == 429:
                    # Rate limited - wait and retry
                    retry_after = (await resp.json()).get('retry_after', 5)
                    print(f"[{alias}] Rate limited, waiting {retry_after}s")
                    await asyncio.sleep(retry_after)
                    continue
                else:
                    print(f"[{alias}] Failed: HTTP {resp.status}")
                    # If token is invalid, stop this token
                    if resp.status == 401:
                        print(f"[{alias}] Token invalid, stopping.")
                        break
        except Exception as e:
            print(f"[{alias}] Error: {e}")
        
        await asyncio.sleep(delay)
    
    print(f"[{alias}] Finished (sent {sent} messages)")

async def main():
    if not TOKENS:
        print("No tokens provided. Exiting.")
        return
    
    print(f"Starting spam with {len(TOKENS)} tokens...")
    print(f"Channel: {CHANNEL_ID}")
    print(f"Message: {MESSAGE}")
    print(f"Delay: {DELAY}s per token")
    if MAX_MESSAGES:
        print(f"Max messages per token: {MAX_MESSAGES}")
    else:
        print("Infinite mode (press Ctrl+C to stop)")
    
    # Assign proxies to tokens (rotate if fewer proxies than tokens)
    proxy_list = PROXIES or [None] * len(TOKENS)
    # If proxies list is shorter, recycle
    if len(proxy_list) < len(TOKENS):
        proxy_list = proxy_list * (len(TOKENS) // len(proxy_list) + 1)
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for idx, token in enumerate(TOKENS):
            # Use token's first 8 chars as alias
            alias = token[:8]
            proxy = proxy_list[idx % len(PROXIES)] if PROXIES else None
            task = asyncio.create_task(
                send_messages(session, token, alias, CHANNEL_ID, MESSAGE, DELAY, MAX_MESSAGES, proxy)
            )
            tasks.append(task)
            # Stagger start to avoid burst login detection
            await asyncio.sleep(0.5)
        
        # Wait for all tasks to complete (or until KeyboardInterrupt)
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("\nStopping... (cancelling tasks)")
            for t in tasks:
                t.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            print("Stopped.")

if __name__ == "__main__":
    asyncio.run(main())
