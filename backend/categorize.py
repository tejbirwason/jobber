from typing import List

from common import app
from modal import Image, Secret
from prompts import (
    get_categorization_prompt,
    sample_jobs,
)
from pydantic import BaseModel, Field
from utils import litellm_completion, track_cost_callback


class JobListing(BaseModel):
    id: str = Field(..., description="The provided ID of the job listing")
    category: str = Field(
        ...,
        description="Category of the job listing",
    )
    explanation: List[str] = Field(..., description="List of reasons explaining the categorization")


class CategorizedListings(BaseModel):
    listings: List[JobListing] = Field(..., description="List of categorized job listings")


def categorize_jobs(jobs=sample_jobs):
    """
    Main function to categorize a list of jobs.
    It prepares job listings, calls the batch categorization, and merges results.
    """
    job_listings = [
        {
            "id": job["id"],
            "title": job["title"],
            "company": job["company"],
            **({"description": job.get("description_text") or job.get("description_html", "")}),
        }
        for job in jobs
    ]

    print(f"Prepared {len(job_listings)} job listings for LLM request")
    response = categorize_jobs_batch(job_listings)

    categorized_jobs = []
    for listing in response:
        try:
            job = next(job for job in jobs if job["id"] == listing.id)
            job["category"] = listing.category
            job["category_explanation"] = listing.explanation
            categorized_jobs.append(job)
        except StopIteration:
            print(f"Warning: No matching job found for listing ID {listing.id}")

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

    batches = [job_listings[i : i + batch_size] for i in range(0, total_listings, batch_size)]
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
    secrets=[
        Secret.from_name("anthropic"),
        Secret.from_name("openai"),
    ],
    retries=3,
)
def categorize_job_listings(job_listings):
    """
    Remote function to categorize job listings using LLM.
    It prepares the input, calls the LLM, and returns categorized results.
    """
    import json

    job_listings_json = json.dumps(job_listings)
    content = get_categorization_prompt(job_listings_json)

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
    categorize_jobs()
