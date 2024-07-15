import logging

from playwright.async_api import Playwright

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = "7230321353:AAFJkYp1QvtN77f737ffvuLzdud199oAtxU"
TELEGRAM_CHAT_ID = "5867217420"


def send_telegram_message(job):
    import requests

    message = f"{job['title']} - {job['company']}\n{job['link']}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        logger.info("Telegram message sent successfully")
    else:
        logger.error(f"Failed to send Telegram message. Status: {response.status_code}")


async def get_undetected_page(playwright: Playwright):
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        java_script_enabled=True,
        locale="en-US",
        timezone_id="America/New_York",
        geolocation={"latitude": 40.7128, "longitude": -74.0060},
        permissions=["geolocation"],
    )
    page = await context.new_page()
    await page.evaluate(
        """
        () => {
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        }
    """
    )
    # Add headers to mimic a real browser
    await page.set_extra_http_headers(
        {
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.google.com/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }
    )

    # Simulate human-like behavior
    await page.mouse.move(x=100, y=100)
    await page.mouse.down()
    await page.mouse.move(x=200, y=200)
    await page.mouse.up()

    return page, browser


def extract_job_info(html_content):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, "html.parser")
    job_cards = soup.find_all("div", class_="cardOutline")

    jobs = []
    stop_scraping = False
    for card in job_cards:
        title_elem = card.find("h2", class_="jobTitle")
        company_elem = card.find("span", {"data-testid": "company-name"})
        location_elem = card.find("div", {"data-testid": "text-location"})
        link_elem = card.find("a", class_="jcs-JobTitle")
        date_elem = card.find("span", {"data-testid": "myJobsStateDate"})

        if title_elem and company_elem and location_elem and link_elem and date_elem:
            title = title_elem.text.strip()
            company = company_elem.text.strip()
            location = location_elem.text.strip()
            link = "https://www.indeed.com" + link_elem["href"]
            job_id = link_elem.get("data-jk", "N/A")
            date_posted = date_elem.text.strip()

            if "Just posted" not in date_posted:
                stop_scraping = True

            jobs.append(
                {
                    "id": job_id,
                    "title": title,
                    "company": company,
                    "location": location,
                    "link": link,
                    "date_posted": date_posted,
                }
            )

        if stop_scraping:
            break

    return jobs, stop_scraping


async def get_next_page_url(page):
    next_button = await page.query_selector('a[data-testid="pagination-page-next"]')
    if next_button:
        return await next_button.get_attribute("href")
    return None
