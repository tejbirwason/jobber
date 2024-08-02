from typing import List, Optional

from common import app
from modal import Image, Secret
from prompts import get_job_description_summary_prompt, sample_jobs
from pydantic import BaseModel, Field
from utils import litellm_completion, track_cost_callback


class JobSummary(BaseModel):
    job_id: str = Field(None, description="Job ID")
    team_information: Optional[List[str]] = Field(None, description="Summary of team information")
    product_information: Optional[List[str]] = Field(None, description="Summary of product information")
    technology_stack: Optional[List[str]] = Field(None, description="Summary of technology stack")
    key_responsibilities: Optional[List[str]] = Field(None, description="Summary of key responsibilities")
    requirements: Optional[List[str]] = Field(None, description="Summary of job requirements")
    exceptional_perks: Optional[List[str]] = Field(None, description="Summary of exceptional perks or benefits")


class JobSummaries(BaseModel):
    job_summaries: List[JobSummary] = Field(..., description="List of job summaries")


def summarize_job_descriptions(jobs=sample_jobs, batch_size=5):
    """
    Summarize job descriptions in batches.
    """
    job_data = [
        {
            "id": job["id"],
            "title": job["title"],
            "description": job.get("description_text") or job.get("description_html", ""),
        }
        for job in jobs
    ]

    print(f"Preparing to summarize {len(job_data)} job descriptions")

    batches = [job_data[i : i + batch_size] for i in range(0, len(job_data), batch_size)]
    print(f"Created {len(batches)} batches for processing")

    batch_results = summarize_batch.map(batches)

    summarized_jobs = []
    for batch_result in batch_results:
        parsed_result = JobSummaries.parse_raw(batch_result)
        summarized_jobs.extend(parsed_result.job_summaries)

    print(f"Summarized {len(summarized_jobs)} job descriptions")
    return summarized_jobs


@app.function(
    image=Image.debian_slim().pip_install("instructor", "litellm"),
    secrets=[
        Secret.from_name("anthropic"),
        Secret.from_name("openai"),
    ],
    retries=3,
)
def summarize_batch(jobs):
    """
    Remote function to summarize a batch of job descriptions using LLM.
    """
    import json

    response = litellm_completion(
        model="gpt-4o-mini",
        content=get_job_description_summary_prompt(json.dumps(jobs)),
        response_model=JobSummaries,
        callback=track_cost_callback,
    )

    return response.json()


@app.local_entrypoint()
def test_summarize_job_descriptions():
    summarized = summarize_job_descriptions()
    print(summarized)
