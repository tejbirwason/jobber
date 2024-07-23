from common import app
from dice.utils import ensure_remote_checkbox_checked, extract_jobs
from modal import Image


@app.function(image=Image.debian_slim(python_version="3.10"))
def scrape_dice_job_descriptions(jobs):
    print(f"Enriching {len(jobs)} jobs with descriptions...")

    result = list(scrape_dice_job_description.map(jobs))

    for job in result:
        print(f"Enriched job: {job['title']} / {job['company']}")

    print(f"Enriched {len(result)} jobs with descriptions!")

    return result


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
    .pip_install("boto3", "beautifulsoup4", "requests"),
    retries=3,
)
async def scrape_dice_job_description(
    job={
        "title": "Software Engineer",
        "link": "https://www.dice.com/job-detail/fe6b9f9d-10fc-454e-81cd-5f1e67e08538",
    },
):
    from bs4 import BeautifulSoup
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        try:
            await page.goto(job["link"], timeout=30000)
            await page.wait_for_load_state("networkidle", timeout=20000)

            html_content = await page.content()
            soup = BeautifulSoup(html_content, "html.parser")

            # Try to find the innermost job description div
            description_elem = soup.select_one('[data-testid="jobDescriptionHtml"]')

            if description_elem:
                # Preserve the HTML content
                description_html = str(description_elem)
                # Also keep the text version for easier processing if needed
                description_text = description_elem.get_text(strip=True, separator="\n")
            else:
                print(f"Could not find job description for {job['title']}")
                description_html = "<p>Description not found</p>"
                description_text = "Description not found"

            enriched_job = {
                **job,
                "description_html": description_html,
                "description_text": description_text,
            }

            print(f"Scraped job description: {job['title']}")
            return enriched_job

        except Exception as e:
            print(f"Error scraping job description: {str(e)}")
            raise
        finally:
            await browser.close()


@app.function(
    timeout=1800,
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
)
async def scrape_dice():
    from bs4 import BeautifulSoup
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        base_url = "https://www.dice.com/jobs?q=software%20engineer&countryCode=US&radius=30&radiusUnit=mi&pageSize=100&filters.postedDate=ONE&filters.employmentType=FULLTIME&language=en"

        print(f"Navigating to Dice URL: {base_url}")
        await page.goto(base_url)
        print("Waiting for network idle after initial page load")
        await page.wait_for_load_state("networkidle")

        await ensure_remote_checkbox_checked(page)
        print("Waiting for network idle after ensuring remote checkbox")
        await page.wait_for_load_state("networkidle")

        all_jobs = []
        while True:
            print("Scraping page")
            print("Waiting for network idle before extracting content")
            await page.wait_for_load_state("networkidle")

            html_content = await page.content()
            soup = BeautifulSoup(html_content, "html.parser")
            jobs = await extract_jobs(soup)
            print(f"Extracted {len(jobs)} jobs from current page")
            all_jobs.extend(jobs)

            next_button = await page.query_selector(
                "li.pagination-next:not(.disabled) a"
            )
            if not next_button:
                print("No more pages to scrape")
                break

            print("Clicking next page")
            await next_button.click()
            await page.wait_for_load_state("networkidle")

        await browser.close()
        print(f"Browser closed. Total jobs scraped: {len(all_jobs)}")

    return all_jobs
