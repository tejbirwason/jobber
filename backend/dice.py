def filter_new_jobs(jobs):
    import os

    import boto3
    from boto3.dynamodb.conditions import Key

    dynamodb = boto3.resource(
        "dynamodb",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name="us-east-1",
    )
    table = dynamodb.Table("jobs")
    new_jobs = []
    for job in jobs:
        response = table.query(
            KeyConditionExpression=Key("website_jobid").eq(job["id"])
        )
        if not response["Items"]:
            new_jobs.append(job)
    return new_jobs


def add_jobs(jobs):
    import os
    from datetime import datetime

    import boto3

    dynamodb = boto3.resource(
        "dynamodb",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name="us-east-1",
    )
    table = dynamodb.Table("jobs")
    for job in jobs:
        new_job = {"website_jobid": job["id"], "timestamp": str(datetime.now()), **job}
        table.put_item(Item=new_job)


async def scrape_dice_page(url, logger):
    from bs4 import BeautifulSoup
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        base_url = "https://www.dice.com/jobs?q=software%20engineer&countryCode=US&radius=30&radiusUnit=mi&pageSize=100&filters.postedDate=ONE&filters.employmentType=FULLTIME&language=en"

        logger.info(f"Navigating to Dice URL: {base_url}")
        await page.goto(base_url)
        await page.wait_for_load_state("networkidle")

        await ensure_remote_checkbox_checked(page, logger)
        await page.wait_for_load_state("networkidle")

        all_jobs = []
        while True:
            logger.info("Scraping page")
            await page.wait_for_load_state("networkidle")

            html_content = await page.content()
            soup = BeautifulSoup(html_content, "html.parser")
            jobs = await extract_jobs(soup, logger)
            all_jobs.extend(jobs)

            next_button = await page.query_selector(
                "li.pagination-next:not(.disabled) a"
            )
            if not next_button:
                logger.info("No more pages to scrape")
                break

            logger.info("Clicking next page")
            await next_button.click()
            await page.wait_for_load_state("networkidle")

        await browser.close()
        logger.info(f"Browser closed. Total jobs scraped: {len(all_jobs)}")

    return all_jobs


# Check if the remote option is selected
async def ensure_remote_checkbox_checked(page, logger):
    remote_checkbox = await page.query_selector(
        'button[aria-label="Filter Search Results by Remote"]'
    )
    if remote_checkbox:
        is_checked = await remote_checkbox.evaluate(
            'el => el.querySelector("i").classList.contains("fa-check-square-o")'
        )
        if not is_checked:
            await remote_checkbox.click()
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(1000)  # Wait for 1 second

            is_checked_after = await remote_checkbox.evaluate(
                'el => el.querySelector("i").classList.contains("fa-check-square-o")'
            )
            if is_checked_after:
                logger.info("Remote checkbox has been checked.")
            return True
    return False


async def extract_jobs(soup, logger):
    job_cards = soup.find_all("dhi-search-card")
    jobs = []

    for card in job_cards:
        title_element = card.find("h5")
        title = title_element.text.strip() if title_element else "N/A"

        title_link_element = card.find("a", {"data-cy": "card-title-link"})
        job_id = title_link_element.get("id") if title_link_element else "N/A"
        title_link = (
            f"https://www.dice.com/job-detail/{job_id}" if job_id != "N/A" else "N/A"
        )

        company_element = card.find("a", {"data-cy": "search-result-company-name"})
        company = company_element.text.strip() if company_element else "N/A"
        company_link = company_element.get("href", "N/A") if company_element else "N/A"

        location_element = card.find("span", {"data-cy": "search-result-location"})
        location = location_element.text.strip() if location_element else "N/A"

        employment_type_element = card.find(
            "span", {"data-cy": "search-result-employment-type"}
        )
        employment_type = (
            employment_type_element.text.strip() if employment_type_element else "N/A"
        )

        posted_date_element = card.find("span", {"data-cy": "card-posted-date"})
        posted_date = posted_date_element.text.strip() if posted_date_element else "N/A"

        company_image_element = card.find("img", {"data-cy": "card-logo"})
        company_image = (
            company_image_element.get("src", "N/A") if company_image_element else "N/A"
        )

        logger.info(f"Scraped job: {title} / {company}")

        job = {
            "id": "dice" + "_" + job_id,
            "title": title,
            "link": title_link,
            "company": company,
            "company_link": company_link,
            "company_image": company_image,
            "location": location,
            "employment_type": employment_type,
            "posted_date": posted_date,
        }
        jobs.append(job)

    return jobs
