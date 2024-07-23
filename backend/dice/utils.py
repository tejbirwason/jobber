def filter_new_jobs(jobs):
    import os

    import boto3
    from boto3.dynamodb.conditions import Key

    print("Initializing DynamoDB resource for filtering new jobs")
    dynamodb = boto3.resource(
        "dynamodb",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name="us-east-1",
    )
    table = dynamodb.Table("jobs")

    print(f"Checking {len(jobs)} jobs against existing entries in DynamoDB")
    existing_job_ids = set()
    for job in jobs:
        response = table.query(
            KeyConditionExpression=Key("id").eq(job["id"]), ProjectionExpression="id"
        )
        if response["Items"]:
            existing_job_ids.add(job["id"])

    new_jobs = [job for job in jobs if job["id"] not in existing_job_ids]
    print(f"Found {len(new_jobs)} new jobs out of {len(jobs)} total jobs")

    return new_jobs


def add_jobs(jobs):
    import os
    from datetime import datetime

    import boto3

    print("Initializing DynamoDB resource")
    dynamodb = boto3.resource(
        "dynamodb",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name="us-east-1",
    )
    table = dynamodb.Table("jobs")

    # Remove duplicates
    unique_jobs = {job["id"]: job for job in jobs}.values()

    batch_size = 25
    batch_items = []

    print(f"Starting to add {len(unique_jobs)} unique jobs...")
    for job in unique_jobs:
        new_job = {"id": job["id"], "timestamp": str(datetime.now()), **job}
        batch_items.append({"PutRequest": {"Item": new_job}})

        if len(batch_items) == batch_size:
            print(f"Writing batch of {len(batch_items)} items to DynamoDB")
            with table.batch_writer() as batch:
                for item in batch_items:
                    batch.put_item(Item=item["PutRequest"]["Item"])
            batch_items = []

    # Write any remaining items
    if batch_items:
        print(f"Writing final batch of {len(batch_items)} items to DynamoDB")
        with table.batch_writer() as batch:
            for item in batch_items:
                batch.put_item(Item=item["PutRequest"]["Item"])

    print("Finished adding all unique jobs to DynamoDB")


# Check if the remote option is selected
async def ensure_remote_checkbox_checked(page):
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
                print("Remote checkbox has been checked.")
            return True
    return False


async def extract_jobs(soup):
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
