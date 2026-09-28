# language: Python 3.11+, file: actions/feed.py
from playwright.async_api import Page
from utils import human_delay, scroll_feed, log
import asyncio
import random


async def like_feed_posts(page: Page, cfg: dict, count: int = None) -> int:
    """like posts on home feed — skips already-liked"""
    count = count or cfg["limits"]["likes_per_session"]
    liked = 0

    await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
    await human_delay(cfg)

    for _ in range(count * 2):  # scroll budget
        await scroll_feed(page, steps=1)

        like_buttons = await page.query_selector_all(
            'button[aria-label^="React Like"]'
        )

        for btn in like_buttons:
            if liked >= count:
                return liked
            try:
                pressed = await btn.get_attribute("aria-pressed")
                if pressed == "false":
                    await btn.scroll_into_view_if_needed()
                    await asyncio.sleep(random.uniform(0.3, 0.9))
                    await btn.click()
                    liked += 1
                    log.info(f"liked post ({liked}/{count})")
                    await human_delay(cfg, multiplier=0.7)
            except Exception as e:
                log.debug(f"like skip: {e}")

    return liked


async def comment_on_feed(page: Page, cfg: dict, count: int = None) -> int:
    """comment on feed posts using template pool"""
    count = count or cfg["limits"]["comments_per_session"]
    templates = cfg["targets"]["comment_templates"]
    commented = 0

    await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
    await human_delay(cfg)

    for _ in range(count * 3):
        await scroll_feed(page, steps=1)

        comment_buttons = await page.query_selector_all(
            'button[aria-label*="comment"]'
        )

        for btn in comment_buttons:
            if commented >= count:
                return commented
            try:
                await btn.scroll_into_view_if_needed()
                await asyncio.sleep(random.uniform(0.5, 1.2))
                await btn.click()
                await asyncio.sleep(1.2)

                # contenteditable comment box
                box = await page.query_selector(
                    'div[contenteditable="true"][data-placeholder*="comment"]'
                )
                if not box:
                    continue

                text = random.choice(templates)
                await box.click()
                for char in text:
                    await page.keyboard.type(char)
                    await asyncio.sleep(random.uniform(0.04, 0.14))

                await asyncio.sleep(0.8)
                # submit
                await page.keyboard.press("Control+Return")
                commented += 1
                log.info(f"commented ({commented}/{count}): {text[:40]}…")
                await human_delay(cfg, multiplier=1.2)

            except Exception as e:
                log.debug(f"comment skip: {e}")

    return commented