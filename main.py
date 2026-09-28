# language: Python 3.11+, file: main.py, target: LinkedIn web
# orchestrates login → action sequence → rate-limited session
import asyncio
from playwright.async_api import async_playwright

from utils import load_config, log
from browser import build_context, new_page
from auth import login
from actions.feed import like_feed_posts, comment_on_feed
from actions.follow import follow_from_search, connect_with_profile
from actions.post import create_post


async def run():
    cfg = load_config()

    async with async_playwright() as pw:
        context = await build_context(pw)
        page = await new_page(context)

        if not await login(page, cfg):
            log.error("cannot proceed without auth")
            await context.close()
            return

        # --- action sequence — comment / uncomment what you need ---

        # like posts
        liked = await like_feed_posts(page, cfg)
        log.info(f"session liked: {liked}")

        # comment on posts
        commented = await comment_on_feed(page, cfg)
        log.info(f"session commented: {commented}")

        # follow people by search keyword
        for kw in cfg["targets"]["search_keywords"]:
            followed = await follow_from_search(page, cfg, keyword=kw, max_follows=10)
            log.info(f"followed {followed} for keyword '{kw}'")

        # publish a post
        await create_post(page, "Thoughts on building in 2026: ship the ugly version first.", cfg)

        # send a connection request to a specific profile
        # await connect_with_profile(page, "https://www.linkedin.com/in/someprofile/", cfg, note="Hi, great content.")

        await context.close()
        log.info("session complete")


if __name__ == "__main__":
    asyncio.run(run())