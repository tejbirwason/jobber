from common import app
from modal import Image
from yc.utils import (
    login,
    scrape_company_logo,
    scrape_company_name,
    scrape_description,
    scrape_job_title,
    scrape_jobs,
    scrape_location,
)


@app.function(
    image=Image.debian_slim(python_version="3.10")
    .run_commands(  # Doesn't work with 3.11 yet
        "apt-get update",
        "apt-get install -y software-properties-common",
        "apt-add-repository non-free",
        "apt-add-repository contrib",
        "pip install playwright==1.44.0",
        "playwright install-deps chromium",
        "playwright install chromium",
    )
    .pip_install("requests"),
    retries=3,
)
async def scrape_yc_job_description(url="https://www.workatastartup.com/jobs/64355"):
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto(url)
        await page.wait_for_load_state("networkidle")

        job_info = {
            "company_logo": await scrape_company_logo(page),
            "title": await scrape_job_title(page),
            "company": await scrape_company_name(page),
            "company_location": await scrape_location(page),
            **await scrape_description(page),
        }

        await browser.close()
        return job_info


@app.function(
    image=Image.debian_slim(python_version="3.10")
    .run_commands(  # Doesn't work with 3.11 yet
        "apt-get update",
        "apt-get install -y software-properties-common",
        "apt-add-repository non-free",
        "apt-add-repository contrib",
        "pip install playwright==1.44.0",
        "playwright install-deps chromium",
        "playwright install chromium",
    )
    .pip_install("requests"),
    retries=3,
)
async def scrape_yc(
    url="https://www.workatastartup.com/companies?demographic=any&hasEquity=any&hasSalary=any&industry=any&interviewProcess=any&jobType=fulltime&layout=list-compact&minExperience=3&minExperience=6&remote=yes&remote=only&role=eng&sortBy=created_desc&tab=any&usVisaNotRequired=any",
    scroll_page=False,
):
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await login(page, url)
        jobs = await scrape_jobs(page, scroll_page)

        await browser.close()
        return jobs


# @app.local_entrypoint()
# def main():
#     # scrape_yc.remote()
#     scrape_yc_job_description.remote()
