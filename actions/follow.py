# language: Python 3.11+, file: actions/follow.py
from playwright.async_api import Page
from utils import human_delay, scroll_feed, log
import asyncio
import random


async def follow_from_search(page: Page, cfg: dict, keyword: str, max_follows: int = None) -> int:
    """
    search keyword → iterate profile cards → click Follow
    skips Connect buttons (different flow, separate action)
    """
    max_follows = max_follows or cfg["limits"]["follows_per_session"]
    count = 0

    encoded = keyword.replace(" ", "%20")
    await page.goto(
        f"https://www.linkedin.com/search/results/people/?keywords={encoded}",
        wait_until="domcontentloaded"
    )
    await human_delay(cfg)

    for attempt in range(5):  # paginate up to 5 pages
        await scroll_feed(page, steps=2)

        # follow buttons in search results
        buttons = await page.query_selector_all('button[aria-label^="Follow"]')
        log.info(f"page {attempt+1}: found {len(buttons)} follow buttons")

        for btn in buttons:
            if count >= max_follows:
                return count
            try:
                await btn.scroll_into_view_if_needed()
                await asyncio.sleep(random.uniform(0.5, 1.2))
                label = await btn.get_attribute("aria-label")
                if label and "Follow" in label and "Unfollow" not in label:
                    await btn.click()
                    count += 1
                    log.info(f"followed ({count}/{max_follows}): {label}")
                    await human_delay(cfg)
            except Exception as e:
                log.warning(f"follow click failed: {e}")
                continue

        # next page
        next_btn = await page.query_selector('button[aria-label="Next"]')
        if next_btn:
            await next_btn.click()
            await human_delay(cfg, multiplier=1.5)
        else:
            break

    return count


async def connect_with_profile(page: Page, profile_url: str, cfg: dict, note: str = "") -> bool:
    """navigate to profile, send connection request with optional note"""
    await page.goto(profile_url, wait_until="domcontentloaded")
    await human_delay(cfg)

    # primary connect button
    connect_btn = await page.query_selector('button[aria-label^="Connect"]')
    if not connect_btn:
        # might be under "More" menu
        more_btn = await page.query_selector('button[aria-label="More actions"]')
        if more_btn:
            await more_btn.click()
            await asyncio.sleep(1)
            connect_btn = await page.query_selector('div[aria-label^="Connect"]')

    if not connect_btn:
        log.warning(f"no connect button found at {profile_url}")
        return False

    await connect_btn.click()
    await asyncio.sleep(1.5)

    if note:
        add_note_btn = await page.query_selector('button[aria-label="Add a note"]')
        if add_note_btn:
            await add_note_btn.click()
            await asyncio.sleep(0.8)
            textarea = await page.query_selector('textarea[name="message"]')
            if textarea:
                await textarea.click()
                for char in note:
                    await page.keyboard.type(char)
                    await asyncio.sleep(random.uniform(0.04, 0.12))

    send_btn = await page.query_selector('button[aria-label="Send invitation"]')
    if send_btn:
        await send_btn.click()
        log.info(f"connection request sent: {profile_url}")
        await human_delay(cfg)
        return True

    return False