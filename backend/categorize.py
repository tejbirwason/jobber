from common import app
from modal import Image, Secret
from prompts import CategorizedListings, get_prompt, sample_jobs
from utils import litellm_completion


def categorize_jobs(jobs):
    """
    Main function to categorize a list of jobs.
    It prepares job listings, calls the batch categorization, and merges results.
    """
    job_listings = [
        {
            "id": job["id"],
            "title": job["title"],
            "company": job["company"],
            **({"description": job["description"]} if "description" in job else {}),
        }
        for job in jobs
    ]

    print(f"Prepared {len(job_listings)} job listings for LLM request")
    response = categorize_jobs_batch(job_listings)

    categorized_jobs = []
    for listing in response:
        job = next(job for job in jobs if job["id"] == listing.id)
        job["category"] = listing.category
        job["category_explanation"] = listing.explanation
        categorized_jobs.append(job)

    print(f"Categorized {len(categorized_jobs)} jobs")
    return categorized_jobs


def categorize_jobs_batch(job_listings=sample_jobs, batch_size=20):
    """
    Function to categorize jobs in batches.
    It processes job listings in smaller batches and aggregates results.
    """
    categorized_listings = []
    total_listings = len(job_listings)

    print(f"Starting batch categorization of {total_listings} job listings")

    batches = [
        job_listings[i : i + batch_size] for i in range(0, total_listings, batch_size)
    ]
    print(f"Created {len(batches)} batches for processing")

    batch_results = categorize_job_listings.map(batches)

    categorized_listings = []
    for batch_result in batch_results:
        parsed_result = CategorizedListings.parse_raw(batch_result)
        categorized_listings.extend(parsed_result.listings)

    print(f"Categorized {len(categorized_listings)} jobs")

    return categorized_listings


@app.function(
    image=Image.debian_slim().pip_install("instructor", "litellm"),
    secrets=[Secret.from_name("anthropic"), Secret.from_name("openai")],
    retries=3,
)
def categorize_job_listings(job_listings):
    """
    Remote function to categorize job listings using LLM.
    It prepares the input, calls the LLM, and returns categorized results.
    """
    import json

    def track_cost_callback(kwargs, completion_response, start_time, end_time):
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
                isinstance(completion_response, litellm.ModelResponse)
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

    job_listings_json = json.dumps(job_listings)
    content = get_prompt(job_listings_json)

    print(f"Calling LLM with {len(job_listings)} job listings...")

    response = litellm_completion(
        model="gpt-4o-mini",
        content=content,
        response_model=CategorizedListings,
        callback=track_cost_callback,
    )

    return response.json()


@app.local_entrypoint()
def main():
    categorize_jobs_batch()
