from common import app
from modal import Image, Secret


@app.function(
    secrets=[Secret.from_name("aws")],
    timeout=1800,
    image=Image.debian_slim().pip_install("boto3", "python-jobspy"),
)
def scrape_jobs(site_name):
    import pandas as pd
    from jobspy import scrape_jobs

    jobs = scrape_jobs(
        site_name=[site_name],
        search_term="software engineer",
        location="Remote",
        results_wanted=1000,
        is_remote=True,
        hours_old=3,
        country_indeed="USA",
    )
    # ['id', 'site', 'job_url', 'job_url_direct', 'title', 'company',
    #    'location', 'job_type', 'date_posted', 'salary_source', 'interval',
    #    'min_amount', 'max_amount', 'currency', 'is_remote', 'job_level',
    #    'job_function', 'company_industry', 'listing_type', 'emails',
    #    'description', 'company_url', 'company_url_direct', 'company_addresses',
    #    'company_num_employees', 'company_revenue', 'company_description',
    #    'logo_photo_url', 'banner_photo_url', 'ceo_name', 'ceo_photo_url']

    def extract_job_data(job):
        return {
            "id": f"{site_name}_{job['id']}",
            "title": job["title"] if not pd.isna(job["title"]) else "",
            "company": job["company"] if not pd.isna(job["company"]) else "",
            "description_text": job["description"] if not pd.isna(job["description"]) else "",
            "link": job["job_url"] if not pd.isna(job["job_url"]) else "",
            "company_link": job["company_url"] if not pd.isna(job["company_url"]) else "",
            "location": job["location"] if not pd.isna(job["location"]) else "",
        }

    return [extract_job_data(job) for _, job in jobs.iterrows()]
