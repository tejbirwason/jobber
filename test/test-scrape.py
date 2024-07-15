import asyncio

from bs4 import BeautifulSoup
from playwright.async_api import Playwright, async_playwright


async def get_undetected_page(playwright: Playwright):
    browser = await playwright.chromium.launch()
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    page = await context.new_page()
    return page, browser


def extract_job_info(html_content):
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


async def scrape_indeed():
    async with async_playwright() as p:
        page, browser = await get_undetected_page(p)

        base_url = "https://www.indeed.com"
        current_url = "/jobs?q=software+engineer&sc=0kf%3Aattr%28DSQF7%29jt%28fulltime%29%3B&rbl=Remote&jlid=aaa2b906602aa8f5&sort=date&vjk=2b374642a1d680ba"

        # Wait for JavaScript to load content
        await page.wait_for_load_state("networkidle")
        page_num = 1

        while current_url:
            full_url = base_url + current_url
            await page.goto(full_url)

            # Wait for JavaScript to load content
            await page.wait_for_load_state("networkidle")

            # Get the HTML content
            html_content = await page.content()

            # Extract job information
            jobs, stop_scraping = extract_job_info(html_content)

            # Print the extracted information
            print(f"\n--- Page {page_num} ---")
            for job in jobs:
                print(f"Job ID: {job['id']}")
                print(f"Title: {job['title']}")
                print(f"Company: {job['company']}")
                print(f"Location: {job['location']}")
                print(f"{job['date_posted']}")
                print(f"Link: {job['link']}")
                print("---")
            print("\n")

            if stop_scraping:
                print(
                    "Encountered a job posted 1 day ago or earlier. Stopping the scrape."
                )
                break

            # Get the URL for the next page
            next_url = await get_next_page_url(page)
            if next_url:
                current_url = next_url
                page_num += 1
                await asyncio.sleep(2)  # Add a delay to be respectful to the website
            else:
                current_url = None

        await browser.close()


# Run the async function
asyncio.run(scrape_indeed())
