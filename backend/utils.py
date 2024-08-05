from common import app
from modal import Image, Secret
from prompts import sample_jobs

TELEGRAM_BOT_TOKEN = "7230321353:AAFJkYp1QvtN77f737ffvuLzdud199oAtxU"
TELEGRAM_CHAT_ID = "5867217420"


def litellm_completion(model, content, response_model, callback):
    import instructor
    import litellm

    litellm.success_callback = [callback]

    client = instructor.from_litellm(litellm.completion)

    return client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[{"role": "user", "content": content}],
        response_model=response_model,
    )


def send_telegram_message(jobs=sample_jobs):
    import requests

    categories = ["Ideal Match", "Strong Potential", "Worth Considering"]
    categorized_jobs = {category: [] for category in categories}

    for job in jobs:
        category = job.get("category")
        if category in categories:
            categorized_jobs[category].append(job)

    if not any(categorized_jobs.values()):
        print("No jobs meet the criteria for sending a Telegram message")
        return

    message = "New Jobs Found:\n"
    for category in categories:
        if len(categorized_jobs[category]) > 0:
            message += f"{len(categorized_jobs[category])} {category}\n"
    message += "\n"

    for category in categories:
        if categorized_jobs[category]:
            message += f"{category}:\n"
            for job in categorized_jobs[category]:
                job_site = (
                    "dice"
                    if job["id"].startswith("dice_")
                    else "indeed"
                    if job["id"].startswith("indeed_")
                    else "yc"
                    if job["id"].startswith("yc_")
                    else "linkedin"
                    if job["id"].startswith("linkedin_")
                    else "glassdoor"
                    if job["id"].startswith("glassdoor_")
                    else "zip_recruiter"
                    if job["id"].startswith("zip_recruiter_")
                    else "unknown"
                )
                message += f"[{job['title']} - {job['company']} ({job_site})]({job['link']})\n"
            message += "\n"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print(f"Telegram message sent successfully with {sum(len(jobs) for jobs in categorized_jobs.values())} jobs")
    else:
        print(f"Failed to send Telegram message. Status: {response.status_code}")


def track_cost_callback(
    kwargs,
    completion_response,
    start_time,
    end_time,
):
    import litellm

    try:
        response_cost = kwargs.get("response_cost", 0)
        duration = end_time - start_time

        print("-" * 40)
        print("LLM Response Summary:")
        print(f"Model: {kwargs['model']}")
        print(f"Cost: ${response_cost:.6f}")
        print(f"Duration: {duration.total_seconds():.2f} seconds")

        if (
            isinstance(
                completion_response,
                litellm.ModelResponse,
            )
            and "usage" in completion_response
        ):
            usage = completion_response["usage"]
            print("Token Usage:")
            print(f"  Completion: {usage.completion_tokens}")
            print(f"  Prompt: {usage.prompt_tokens}")
            print(f"  Total: {usage.total_tokens}")
        print("-" * 40)
    except:
        print("Error occurred while printing LLM response summary")


@app.function(
    secrets=[Secret.from_name("aws")],
    timeout=1800,
    image=Image.debian_slim().pip_install("boto3"),
)
def clear_db(table_name="jobs", region_name="us-east-1"):
    import os

    import boto3

    # Initialize DynamoDB resource
    dynamodb = boto3.resource(
        "dynamodb",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=region_name,
    )
    table = dynamodb.Table(table_name)

    # Scan the table to fetch all jobs
    all_jobs = []
    last_evaluated_key = None

    while True:
        if last_evaluated_key:
            response = table.scan(ExclusiveStartKey=last_evaluated_key)
        else:
            response = table.scan()

        all_jobs.extend(response["Items"])

        last_evaluated_key = response.get("LastEvaluatedKey")
        if not last_evaluated_key:
            break

    print(f"Total jobs fetched: {len(all_jobs)}")

    # Delete all items from the DynamoDB table
    with table.batch_writer() as batch:
        for job in all_jobs:
            batch.delete_item(Key={"id": job["id"]})

    print(f"Deleted {len(all_jobs)} jobs from the table.")


@app.local_entrypoint()
def test_clear_db():
    clear_db.remote()
