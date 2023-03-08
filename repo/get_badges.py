#!python3

import asyncio

from repo_assets import update_version_badge

if __name__ == "__main__":
    asyncio.run(update_version_badge())
