import asyncio

from modal import Image
from utils import (
    extract_job_info,
    get_next_page_url,
    get_undetected_page,
)

from backend.common import app

MAX_RETRIES = 10


@app.function(
    image=Image.debian_slim(python_version="3.10")
    .run_commands(  # Doesn't work with 3.11 yet
        "apt-get update",
        "apt-get install -y software-properties-common",
        "apt-add-repository non-free",
        "apt-add-repository contrib",
        "pip install playwright==1.44.0",
        "playwright install-deps chromium",
        "playwright install chromium",
    )
    .pip_install("beautifulsoup4", "requests"),
    retries=3,
)
async def scrape_indeed(num_pages=1):
    from playwright.async_api import async_playwright

    jobs = []
    async with async_playwright() as p:
        base_url = "https://www.indeed.com"
        current_url = "/jobs?q=software+engineer&sc=0kf%3Aattr%28DSQF7%29jt%28fulltime%29%3B&rbl=Remote&jlid=aaa2b906602aa8f5&sort=date&vjk=2b374642a1d680ba"
        full_url = base_url + current_url

        page, browser = await get_undetected_page(p, full_url)

        for page_num in range(num_pages):
            print(f"Processing page {page_num + 1}: {full_url}")
            html_content = await page.content()
            jobs_on_page = await extract_job_info(page, html_content)
            jobs.extend(jobs_on_page)

            if page_num < num_pages - 1:
                full_url = await navigate_to_next_page(page, base_url)
                if not full_url:
                    print("No more pages available")
                    break

            await asyncio.sleep(2)

        await browser.close()
        print("Browser closed")

    return jobs


async def navigate_to_next_page(page, base_url):
    next_url = await get_next_page_url(page)
    if next_url:
        full_url = base_url + next_url
        await page.goto(full_url, wait_until="networkidle")
        return full_url
    return None


@app.local_entrypoint()
def main():
    scrape_indeed.remote()
