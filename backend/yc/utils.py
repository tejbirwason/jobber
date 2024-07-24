import asyncio


async def login(page, url):
    await page.goto(url)
    await page.wait_for_load_state("networkidle")
    await page.click('text="Log In ›"')
    await page.wait_for_load_state("networkidle")
    await page.fill("#ycid-input", "tejbirwason")
    await page.fill("#password-input", "tejabhai")
    await page.click('button:has-text("Log in")')
    await page.wait_for_load_state("networkidle")
    await asyncio.sleep(10)
    await page.goto(url)
    await page.wait_for_load_state("networkidle")


async def scrape_jobs(page, scroll_page):
    jobs = []
    while True:
        new_jobs = await scrape_job_divs(page)
        if not new_jobs:
            break
        jobs.extend(new_jobs)
        if scroll_page:
            await scroll_page_down(page)
        else:
            break
    print_jobs(jobs)
    return jobs


async def scrape_job_divs(page):
    new_jobs = []
    job_divs = await page.query_selector_all("div.job-name")
    for job_div in job_divs:
        job_link_element = await job_div.query_selector("a")
        if job_link_element:
            job_name = await job_link_element.inner_text()
            job_link = await job_link_element.get_attribute("href")
            job_id = job_link.split("/")[-1] if job_link else None
            job = {
                "id": f"yc_{job_id}" if job_id else None,
                "name": job_name,
                "link": job_link,
            }
            if job["link"] not in [j["link"] for j in new_jobs]:
                new_jobs.append(job)
    return new_jobs


async def scroll_page_down(page):
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(5000)


def print_jobs(jobs):
    print("Scraped Jobs:")
    for index, job in enumerate(jobs, 1):
        print(f"{index}. {job['id']} - {job['name']} - {job['link']}")


async def scrape_company_logo(page):
    logo_element = await page.query_selector(".company-logo img")
    return await logo_element.get_attribute("src") if logo_element else None


async def scrape_job_title(page):
    title_element = await page.query_selector(".company-name")
    if title_element:
        full_title = await title_element.inner_text()
        return full_title.split(" at ")[0].strip() if " at " in full_title else None
    return None


async def scrape_company_name(page):
    title_element = await page.query_selector(".company-name")
    if title_element:
        full_title = await title_element.inner_text()
        return full_title.split(" at ")[1].strip() if " at " in full_title else None
    return None


async def scrape_location(page):
    location_element = await page.query_selector(
        ".company-title .company-details > div:first-child > div"
    )
    if location_element:
        location = await location_element.inner_text()
        return location.replace("", "").strip()
    return None


async def scrape_description(page):
    description_elements = await page.query_selector_all(
        ".bg-beige-lighter > div:not(:first-child)"
    )
    if description_elements:
        description_html = "".join(
            [await elem.inner_html() for elem in description_elements]
        )
        description_text = " ".join(
            [await elem.inner_text() for elem in description_elements]
        )
        return {
            "description_html": description_html,
            "description_text": description_text[:200] if description_text else None,
        }
    return {"description_html": None, "description_text": None}
