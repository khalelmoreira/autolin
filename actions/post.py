# language: Python 3.11+, file: actions/post.py
from playwright.async_api import Page
from utils import human_delay, log
import asyncio
import random


async def create_post(page: Page, text: str, cfg: dict) -> bool:
    """open composer, type post, publish"""
    await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
    await human_delay(cfg)

    # open composer
    start_btn = await page.query_selector('button[aria-label="Start a post"]')
    if not start_btn:
        # fallback selector — LinkedIn changes this periodically
        start_btn = await page.query_selector(
            'div[data-control-name="share.sharebox_open"]'
        )

    if not start_btn:
        log.warning("post composer button not found")
        return False

    await start_btn.click()
    await asyncio.sleep(1.5)

    editor = await page.query_selector('div[contenteditable="true"][role="textbox"]')
    if not editor:
        log.warning("post editor not found after opening composer")
        return False

    await editor.click()
    for char in text:
        await page.keyboard.type(char)
        await asyncio.sleep(random.uniform(0.04, 0.15))

    await asyncio.sleep(1.0)

    post_btn = await page.query_selector('button[aria-label="Post"]')
    if not post_btn:
        log.warning("post submit button not found")
        return False

    await post_btn.click()
    await asyncio.sleep(2.5)
    log.info(f"post published: {text[:60]}…")
    await human_delay(cfg)
    return True