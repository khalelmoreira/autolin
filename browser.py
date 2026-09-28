# language: Python 3.11+, file: browser.py
# playwright-stealth masks: navigator.webdriver, plugins, languages, chrome runtime
from playwright.async_api import async_playwright, BrowserContext, Page
from playwright_stealth import stealth_async
from pathlib import Path
import logging

log = logging.getLogger("linkedin_bot")
SESSION_DIR = Path("session_data")
SESSION_DIR.mkdir(exist_ok=True)


async def build_context(playwright) -> BrowserContext:
    """persistent context — cookies survive restarts, no re-login every run"""
    browser = await playwright.chromium.launch_persistent_context(
        user_data_dir=str(SESSION_DIR),
        headless=False,          # flip True once you've confirmed login
        viewport={"width": 1366, "height": 768},
        locale="en-US",
        timezone_id="America/New_York",
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-sandbox",
        ]
    )
    return browser


async def new_page(context: BrowserContext) -> Page:
    page = await context.new_page()
    await stealth_async(page)   # patches all JS automation signals
    page.set_default_timeout(15_000)
    return page