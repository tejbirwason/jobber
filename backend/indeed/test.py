import asyncio
import random

from playwright.async_api import async_playwright

# from common import app
from utils import get_undetected_page


async def simulate_human_behavior(page):
    # Randomly scroll
    if random.random() < 0.7:
        scroll_amount = random.randint(100, 500)
        await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
        await asyncio.sleep(random.uniform(0.5, 2))

    # Randomly move mouse
    if random.random() < 0.5:
        x = random.randint(0, 1000)
        y = random.randint(0, 1000)
        await page.mouse.move(x, y)
        await asyncio.sleep(random.uniform(0.3, 1))


# @app.function(
#     image=Image.debian_slim(python_version="3.10")
#     .run_commands(  # Doesn't work with 3.11 yet
#         "apt-get update",
#         "apt-get install -y software-properties-common",
#         "apt-add-repository non-free",
#         "apt-add-repository contrib",
#         "pip install playwright==1.44.0",
#         "playwright install-deps chromium",
#         "playwright install chromium",
#     )
#     .pip_install("beautifulsoup4"),
#     timeout=1800,
#     retries=3,
# )
async def scrape_google_jobs():
    async with async_playwright() as p:
        base_url = "https://www.indeed.com"
        current_url = "/jobs?q=software+engineer&sc=0kf%3Aattr%28DSQF7%29jt%28fulltime%29%3B&sort=date"
        url = base_url + current_url

        page, browser = await get_undetected_page(p, url)

        all_jobs = []

        while True:
            print(f"Navigating to Indeed Jobs URL: {url}")
            await page.goto(url)
            await page.wait_for_load_state("networkidle")

            await simulate_human_behavior(page)

            job_divs = await page.query_selector_all("td.resultContent")
            for div in job_divs:
                # Check if the job was not just posted
                just_posted = await div.query_selector(
                    'span[data-testid="myJobsStateDate"]:has-text("Just posted")'
                )
                if not just_posted:
                    print("Found a job that was not just posted. Stopping the scrape.")
                    await browser.close()
                    return all_jobs

                title = await div.query_selector('h2.jobTitle span[id^="jobTitle"]')
                company = await div.query_selector('span[data-testid="company-name"]')
                location = await div.query_selector('div[data-testid="text-location"]')

                title_text = await title.inner_text() if title else "N/A"
                company_text = await company.inner_text() if company else "N/A"
                location_text = await location.inner_text() if location else "N/A"

                print(f"Job listing: {title_text} at {company_text} in {location_text}")

                # Click on the job div to open the description
                await div.click()
                await page.wait_for_load_state("networkidle")

                # Wait a random amount of time after clicking
                await asyncio.sleep(random.uniform(1, 3))

                await simulate_human_behavior(page)

                # Extract the job description
                description_elem = await page.query_selector("#jobDescriptionText")
                description_html = ""
                description_text = ""
                if description_elem:
                    description_html = await description_elem.inner_html()
                    description_text = await description_elem.inner_text()

                # Extract company info
                company_info_elem = await page.query_selector(
                    'div[data-testid="jobsearch-CompanyInfoContainer"]'
                )
                company_name = "N/A"
                company_link = "N/A"
                if company_info_elem:
                    company_name_elem = await company_info_elem.query_selector(
                        'div[data-company-name="true"]'
                    )
                    company_name = (
                        await company_name_elem.inner_text()
                        if company_name_elem
                        else "N/A"
                    )

                    company_link_elem = await company_info_elem.query_selector("a")
                    company_link = (
                        await company_link_elem.get_attribute("href")
                        if company_link_elem
                        else "N/A"
                    )

                # Extract job ID and current URL
                current_url = page.url
                job_id = (
                    current_url.split("&vjk=")[-1] if "&vjk=" in current_url else "N/A"
                )

                # Assemble job information
                job = {
                    "id": job_id,
                    "title": title_text,
                    "company": company_text,
                    "company_link": company_link,
                    "link": current_url,
                    "description_text": description_text,
                    "description_html": description_html,
                    "location": location_text,
                }

                all_jobs.append(job)

            # Check for next page
            next_button = await page.query_selector(
                'a[data-testid="pagination-page-next"]'
            )
            if next_button:
                next_url = await next_button.get_attribute("href")
                url = base_url + next_url
            else:
                break  # No more pages to scrape

            # Randomly decide to take a longer break between pages
            if random.random() < 0.3:
                await asyncio.sleep(random.uniform(5, 10))

        await browser.close()
        return all_jobs


def print_job_details(jobs):
    print(f"Total jobs scraped: {len(jobs)}")
    for job in jobs:
        print(f"Job ID: {job['id']}")
        print(f"Title: {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Company Link: {job['company_link']}")
        print(f"Job Link: {job['link']}")
        print(f"Location: {job['location']}")
        print(f"Description: {job['description_text'][:200]}...")
        print("---")


if __name__ == "__main__":
    jobs = asyncio.run(scrape_google_jobs())
    print_job_details(jobs)


# @app.local_entrypoint()
# def main():
#     jobs = scrape_google_jobs.remote()
#     print_job_details(jobs)
