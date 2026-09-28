# language: Python 3.11+, file: utils.py
import asyncio
import random
import logging
import json
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("linkedin_bot")


def load_config(path: str = "config.json") -> dict:
    with open(path) as f:
        return json.load(f)


async def human_delay(cfg: dict, multiplier: float = 1.0):
    """randomized delay — breaks behavioral fingerprinting"""
    lo = cfg["delays"]["action_min"] * multiplier
    hi = cfg["delays"]["action_max"] * multiplier
    await asyncio.sleep(random.uniform(lo, hi))


async def human_type(page, selector: str, text: str, cfg: dict):
    """character-by-character typing with jitter — avoids paste detection"""
    await page.click(selector)
    for char in text:
        await page.keyboard.type(char)
        await asyncio.sleep(
            random.uniform(
                cfg["delays"]["typing_min"],
                cfg["delays"]["typing_max"]
            )
        )


async def scroll_feed(page, steps: int = 3):
    """scroll to load more posts, humanlike"""
    for _ in range(steps):
        await page.mouse.wheel(0, random.randint(600, 1100))
        await asyncio.sleep(random.uniform(0.8, 1.8))