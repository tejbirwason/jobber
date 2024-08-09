from typing import List, Optional

from common import app
from modal import Image, Secret
from prompts import (
    get_company_description_prompt,
)
from pydantic import BaseModel, Field
from utils import link_jobs_to_companies, litellm_completion, track_cost_callback


def add_company_info_to_dynamodb(company_name, search_results, llm_response):
    import boto3
    from botocore.exceptions import ClientError

    dynamodb = boto3.resource("dynamodb")
    companies_table = dynamodb.Table("companies")

    if company_name:
        try:
            company_info = llm_response.dict()

            companies_table.put_item(
                Item={
                    "name": company_name,
                    "info": company_info,
                    "search_results": search_results,
                    # Add other attributes as needed
                },
                ConditionExpression="attribute_not_exists(#n)",
                ExpressionAttributeNames={"#n": "name"},
            )
            print(f"Successfully added {company_name} to the companies table.")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                print(f"{company_name} already exists in the companies table.")
            else:
                print(f"Error adding {company_name} to the companies table: {e}")
    else:
        print("No company name found in the job data.")


def filter_jobs_needing_enrichment(jobs_to_enrich):
    import boto3

    dynamodb = boto3.resource("dynamodb")

    unique_companies = set(job["company"] for job in jobs_to_enrich if job.get("company"))

    print(f"Fetching {len(unique_companies)} companies from DynamoDB...")

    response = dynamodb.batch_get_item(
        RequestItems={
            "companies": {
                "Keys": [{"name": company} for company in unique_companies],
                "ProjectionExpression": "#n",
                "ExpressionAttributeNames": {"#n": "name"},
            }
        }
    )

    existing_companies = set(item["name"] for item in response["Responses"]["companies"])

    return [job for job in jobs_to_enrich if job.get("company") and job["company"] not in existing_companies]


class KeyLinks(BaseModel):
    official: str = Field(None, description="Official website of the company")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile of the company")
    other: Optional[List[str]] = Field(None, description="Other relevant links")


class CompanyCategoryDetails(BaseModel):
    company_overview: List[str] = Field(None, description="Details about the company overview")
    key_links: KeyLinks = Field(..., description="Details about the company's key links")
    business_description: Optional[List[str]] = Field(None, description="Details about the business description")
    products_services: Optional[List[str]] = Field(None, description="Details about the products or services")
    key_locations: Optional[List[str]] = Field(None, description="Details about the company's key locations")
    history: Optional[List[str]] = Field(None, description="Details about the company's history")
    financials: Optional[List[str]] = Field(None, description="Details about the company's financials")
    leadership: Optional[List[str]] = Field(None, description="Details about the company's leadership")
    technology: Optional[List[str]] = Field(None, description="Details about the company's technology")
    corporate_culture: Optional[List[str]] = Field(None, description="Details about the company's corporate culture")


@app.function(
    secrets=[Secret.from_name("aws"), Secret.from_name("openai")],
    timeout=600,
    image=Image.debian_slim().pip_install("requests", "boto3", "litellm", "instructor"),
)
def fetch_company_info(job):
    import urllib.parse

    import requests

    company = job.get("company", "")
    if company:
        company_query = urllib.parse.quote(f"{company} company")
        url = f"https://s.jina.ai/{company_query}"
        print(f"Searching the web for: {company}...")
        search_response = requests.get(url)
        search_results = search_response.text
        print(f"Company: {company}, Character Count: {len(search_results)}")
    else:
        print("No company information found in the job data.")

    print(f"Calling LLM for job {job['company']}...")

    llm_response = litellm_completion(
        model="gpt-4o-mini",
        content=get_company_description_prompt(search_response.text),
        response_model=CompanyCategoryDetails,
        callback=track_cost_callback,
    )

    add_company_info_to_dynamodb(job["company"], search_results, llm_response)


@app.function(
    secrets=[Secret.from_name("aws")],
    timeout=600,
    image=Image.debian_slim().pip_install("boto3"),
)
def enrich_company_info(jobs):
    print(f"Total jobs: {len(jobs)}")
    filter_categories = ["Strong Potential", "Ideal Match"]
    filtered_jobs = [job for job in jobs if job.get("category") in filter_categories]

    print(f"Categrorized jobs to enrich: {len(filtered_jobs)}")

    jobs_to_enrich = filter_jobs_needing_enrichment(filtered_jobs)

    print(f"Jobs to enrich with company info: {len(jobs_to_enrich)}")

    results = list(fetch_company_info.map(jobs_to_enrich))

    print("Finished fetching company information.")


@app.local_entrypoint()
def test_enrich_company_info():
    import boto3

    print("Fetching some sample jobs...")
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("jobs")

    response = table.scan()
    jobs = response["Items"]
    enrich_company_info.remote(jobs)
    link_jobs_to_companies(jobs)
