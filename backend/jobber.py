from categorize import categorize_jobs
from common import app
from dice.scrape import scrape_dice, scrape_dice_job_descriptions
from dice.utils import add_jobs, filter_new_jobs
from indeed.scrape import scrape_indeed
from modal import Image, Secret
from utils import (
    send_telegram_message,
)
from yc.scrape import scrape_yc, scrape_yc_job_description

# ALWAYS BE APPLYING !!!
# Other job boards: tta, builtin, wellfound / angel list / remotive / Ladders


@app.function(
    secrets=[Secret.from_name("aws")],
    timeout=1800,
    image=Image.debian_slim().pip_install("boto3"),
    retries=3,
)
def scrape_dice_jobs():
    print("Scraping Dice jobs...")
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
        print("Done scraping Dice jobs!")
        return jobs_with_categories
    else:
        print("No new jobs since last scrape. Done!")
        return []


@app.function(
    secrets=[Secret.from_name("aws")],
    timeout=1800,
    image=Image.debian_slim().pip_install("boto3", "requests"),
    retries=3,
)
def scrape_yc_jobs():
    print("Scraping YC jobs...")
    jobs = scrape_yc.remote(scroll_page=False)

    if not jobs:
        print("No YC jobs found during scraping. Done!")
        return

    new_jobs = filter_new_jobs(jobs)

    if new_jobs:
        jobs_with_descriptions = []
        jobs_with_descriptions = list(
            scrape_yc_job_description.map([job["link"] for job in new_jobs])
        )
        jobs_with_descriptions = [
            {**job, **job_info}
            for job, job_info in zip(new_jobs, jobs_with_descriptions)
        ]

        jobs_with_categories = categorize_jobs(jobs_with_descriptions)
        add_jobs(jobs_with_categories)
        print("Done scraping YC jobs!")
        return jobs_with_categories
    else:
        print("No new YC jobs since last scrape. Done!")
        return []


@app.function(
    secrets=[Secret.from_name("aws")],
    timeout=1800,
    image=Image.debian_slim().pip_install("boto3", "python-jobspy"),
    retries=3,
)
def scrape_indeed_jobs():
    print("Scraping Indeed jobs...")
    jobs = scrape_indeed()

    if not jobs:
        print("No Indeed jobs found during scraping. Done!")
        return

    new_jobs = filter_new_jobs(jobs)

    if new_jobs:
        jobs_with_categories = categorize_jobs(new_jobs)
        add_jobs(jobs_with_categories)
        print("Done scraping Indeed jobs!")
        return jobs_with_categories
    else:
        print("No new Indeed jobs since last scrape. Done!")
        return []


@app.function(
    timeout=1800,
    image=Image.debian_slim().pip_install("requests"),
)
def scrape():
    dice_jobs = scrape_dice_jobs.remote()
    yc_jobs = scrape_yc_jobs.remote()
    indeed_jobs = scrape_indeed_jobs.remote()

    all_jobs = dice_jobs + yc_jobs + indeed_jobs
    if all_jobs:
        send_telegram_message(all_jobs)
    else:
        print("No new jobs found across all platforms.")


@app.local_entrypoint()
def test_jobber():
    scrape_indeed_jobs.remote()
