# language: Python 3.11+, file: auth.py
from playwright.async_api import Page
from utils import human_delay, human_type, log
import asyncio


async def is_logged_in(page: Page) -> bool:
    await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
    await asyncio.sleep(2)
    return "feed" in page.url


async def login(page: Page, cfg: dict) -> bool:
    """returns True on success — skips if session cookie already valid"""
    if await is_logged_in(page):
        log.info("session active, skipping login")
        return True

    await page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
    await human_delay(cfg)

    await human_type(page, "#username", cfg["credentials"]["email"], cfg)
    await asyncio.sleep(0.4)
    await human_type(page, "#password", cfg["credentials"]["password"], cfg)
    await asyncio.sleep(0.3)

    await page.click('button[type="submit"]')
    await page.wait_for_load_state("domcontentloaded")
    await asyncio.sleep(3)

    if "feed" in page.url or "checkpoint" not in page.url:
        log.info("login successful")
        return True

    log.warning("login failed or CAPTCHA hit — handle manually")
    return False