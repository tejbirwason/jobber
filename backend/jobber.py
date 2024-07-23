from categorize import categorize_jobs
from common import app
from dice.scrape import scrape_dice, scrape_dice_job_descriptions
from dice.utils import add_jobs, filter_new_jobs
from modal import Image, Period, Secret
from utils import (
    send_telegram_message,
)

# @app.function(
#     # schedule=Period(minutes=60),
#     secrets=[Secret.from_name("aws")],
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
#     .pip_install("boto3", "beautifulsoup4", "requests"),
# )
# async def scrape_and_update_jobs():
#     import boto3
#     from boto3.dynamodb.conditions import Key
#     from playwright.async_api import async_playwright

#     print("Starting scrape_and_update_jobs function")

#     # Initialize DynamoDB client
#     dynamodb = boto3.resource(
#         "dynamodb",
#         aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
#         aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
#         region_name="us-east-1",
#     )

#     # Access the 'jobs' table
#     table = dynamodb.Table("jobs")
#     print(f"Connected to DynamoDB table: {table.table_name}")

#     async with async_playwright() as p:
#         page, browser = await get_undetected_page(p)
#         print("Undetected browser and page initialized")

#         base_url = "https://www.indeed.com"
#         current_url = "/jobs?q=software+engineer&sc=0kf%3Aattr%28DSQF7%29jt%28fulltime%29%3B&rbl=Remote&jlid=aaa2b906602aa8f5&sort=date&vjk=2b374642a1d680ba"

#         while current_url:
#             full_url = base_url + current_url
#             print(f"Navigating to: {full_url}")
#             await page.goto(full_url)
#             await page.wait_for_load_state("networkidle")

#             html_content = await page.content()
#             jobs, stop_scraping = extract_job_info(html_content)
#             print(f"Extracted {len(jobs)} jobs from the page")

#             for job in jobs:
#                 # Check if job already exists
#                 response = table.query(
#                     KeyConditionExpression=Key("website_jobid").eq(
#                         "indeed" + "_" + job["id"]
#                     )
#                 )
#                 if not response["Items"]:
#                     print(f"New job found: {job['title']} at {job['company']}")
#                     # Add new job to the table
#                     new_job = {
#                         "website_jobid": "indeed" + "_" + job["id"],
#                         "timestamp": str(datetime.now()),
#                         "title": job["title"],
#                         "company": job["company"],
#                         "location": job["location"],
#                         "link": job["link"],
#                         "date_posted": job["date_posted"],
#                     }
#                     table.put_item(Item=new_job)
#                     print(f"Added new job to DynamoDB: {job['id']}")
#                     # Send Telegram message for new job
#                     send_telegram_message(new_job)
#                 else:
#                     print(f"Job already exists in DynamoDB: {job['id']}")

#             if stop_scraping:
#                 print("Stop condition met. Ending scraping process.")
#                 break

#             next_url = await get_next_page_url(page)
#             current_url = next_url if next_url else None
#             print(f"Next URL: {current_url}")
#             await asyncio.sleep(2)

#         await browser.close()
#         print("Browser closed")

#     print("Finished scraping and updating jobs table")
#     return "Finished scraping and updating jobs table"


@app.function(
    schedule=Period(minutes=180),
    secrets=[Secret.from_name("aws")],
    timeout=1800,
    image=Image.debian_slim().pip_install("boto3", "requests"),
)
def scrape_dice_jobs():
    jobs = scrape_dice.remote()

    if not jobs:
        print("No jobs found during scraping. Done!")
        return

    # Remove duplicates before filtering new jobs
    unique_jobs = {job["id"]: job for job in jobs}.values()
    new_jobs = filter_new_jobs(unique_jobs)

    if new_jobs:
        jobs_with_descriptions = scrape_dice_job_descriptions.remote(new_jobs)
        jobs_with_categories = categorize_jobs(jobs_with_descriptions)
        add_jobs(jobs_with_categories)
        send_telegram_message(jobs_with_categories)
    else:
        print("No new jobs since last scrape. Done!")

    return
