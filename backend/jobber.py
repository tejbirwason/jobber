import asyncio
import logging
import os
from datetime import datetime

from dice import add_jobs, filter_new_jobs, scrape_dice_page
from modal import App, Image, Period, Secret
from utils import (
    extract_job_info,
    get_next_page_url,
    get_undetected_page,
    send_telegram_message,
)

app = App(name="jobber")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.function(
    schedule=Period(minutes=60),
    secrets=[Secret.from_name("aws")],
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
)
async def scrape_and_update_jobs():
    import boto3
    from boto3.dynamodb.conditions import Key
    from playwright.async_api import async_playwright

    logger.info("Starting scrape_and_update_jobs function")

    # Initialize DynamoDB client
    dynamodb = boto3.resource(
        "dynamodb",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name="us-east-1",
    )

    # Access the 'jobs' table
    table = dynamodb.Table("jobs")
    logger.info(f"Connected to DynamoDB table: {table.table_name}")

    async with async_playwright() as p:
        page, browser = await get_undetected_page(p)
        logger.info("Undetected browser and page initialized")

        base_url = "https://www.indeed.com"
        current_url = "/jobs?q=software+engineer&sc=0kf%3Aattr%28DSQF7%29jt%28fulltime%29%3B&rbl=Remote&jlid=aaa2b906602aa8f5&sort=date&vjk=2b374642a1d680ba"

        while current_url:
            full_url = base_url + current_url
            logger.info(f"Navigating to: {full_url}")
            await page.goto(full_url)
            await page.wait_for_load_state("networkidle")

            html_content = await page.content()
            jobs, stop_scraping = extract_job_info(html_content)
            logger.info(f"Extracted {len(jobs)} jobs from the page")

            for job in jobs:
                # Check if job already exists
                response = table.query(
                    KeyConditionExpression=Key("website_jobid").eq(
                        "indeed" + "_" + job["id"]
                    )
                )
                if not response["Items"]:
                    logger.info(f"New job found: {job['title']} at {job['company']}")
                    # Add new job to the table
                    new_job = {
                        "website_jobid": "indeed" + "_" + job["id"],
                        "timestamp": str(datetime.now()),
                        "title": job["title"],
                        "company": job["company"],
                        "location": job["location"],
                        "link": job["link"],
                        "date_posted": job["date_posted"],
                    }
                    table.put_item(Item=new_job)
                    logger.info(f"Added new job to DynamoDB: {job['id']}")
                    # Send Telegram message for new job
                    send_telegram_message(new_job)
                else:
                    logger.info(f"Job already exists in DynamoDB: {job['id']}")

            if stop_scraping:
                logger.info("Stop condition met. Ending scraping process.")
                break

            next_url = await get_next_page_url(page)
            current_url = next_url if next_url else None
            logger.info(f"Next URL: {current_url}")
            await asyncio.sleep(2)

        await browser.close()
        logger.info("Browser closed")

    logger.info("Finished scraping and updating jobs table")
    return "Finished scraping and updating jobs table"


@app.function(
    schedule=Period(minutes=60),
    secrets=[Secret.from_name("aws")],
    timeout=600,
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
)
async def scrape_dice_jobs():
    url = "https://www.dice.com/jobs?q=software%20engineer&countryCode=US&radius=30&radiusUnit=mi&page=1&pageSize=100&filters.postedDate=ONE&filters.employmentType=FULLTIME&language=en"
    jobs = await scrape_dice_page(url, logger)
    logger.info("Finished scraping Dice jobs page")

    new_jobs = filter_new_jobs(jobs)

    if new_jobs:
        enriched_jobs = scrape_dice_job_descriptions.remote(new_jobs)
        logger.info(f"Enriched {len(enriched_jobs)} new jobs with descriptions")
        add_jobs(enriched_jobs)

        # Send Telegram message for each new job
        for job in enriched_jobs:
            send_telegram_message(job)
            logger.info(f"Sent Telegram message for new job: {job['title']}")
    else:
        logger.info("No new jobs to enrich")

    return f"Finished scraping Dice jobs page. Enriched and added {len(new_jobs)} new jobs."


@app.function(image=Image.debian_slim(python_version="3.10"), timeout=600)
def scrape_dice_job_descriptions(jobs):
    import logging

    logger = logging.getLogger(__name__)

    logger.info("Starting scrape_dice_job_descriptions function")

    result = list(scrape_dice_job_description.map(jobs))

    for job in result:
        logger.info(f"Enriched job: {job['title']} / {job['company']}")

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
)
async def scrape_dice_job_description(job):
    from bs4 import BeautifulSoup
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        try:
            await page.goto(job["link"])
            await page.wait_for_load_state("networkidle")

            html_content = await page.content()
            soup = BeautifulSoup(html_content, "html.parser")

            # Try to find the innermost job description div
            description_elem = soup.select_one('[data-testid="jobDescriptionHtml"]')

            if description_elem:
                description = description_elem.get_text(strip=True, separator="\n")
            else:
                logger.warning(f"Could not find job description for {job['title']}")
                description = "Description not found"

            enriched_job = {**job, "description": description}

            logger.info(f"Enriched job with description: {job['title']}")
            return enriched_job

        except Exception as e:
            logger.error(f"Error scraping job description: {str(e)}")
            return job
        finally:
            await browser.close()
