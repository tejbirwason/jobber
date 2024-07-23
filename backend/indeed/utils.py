import asyncio
import random


async def get_undetected_page(playwright, url):
    MAX_RETRIES = 5
    for attempt in range(MAX_RETRIES):
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{random.randint(10,15)}_{random.randint(1,7)}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(80,90)}.0.{random.randint(4000,5000)}.0 Safari/537.36",
            viewport={
                "width": random.randint(1280, 1920),
                "height": random.randint(800, 1080),
            },
            java_script_enabled=True,
            locale=random.choice(["en-US", "en-GB", "en-CA"]),
            timezone_id=random.choice(
                ["America/New_York", "America/Los_Angeles", "Europe/London"]
            ),
            geolocation={
                "latitude": random.uniform(30, 50),
                "longitude": random.uniform(-120, -70),
            },
            permissions=["geolocation"],
        )
        page = await context.new_page()
        await page.evaluate(
            """
            () => {
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en', 'es']});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            }
        """
        )
        await page.set_extra_http_headers(
            {
                "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": random.choice(
                    [
                        "https://www.google.com/",
                        "https://www.bing.com/",
                        "https://www.duckduckgo.com/",
                    ]
                ),
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "cross-site",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            }
        )

        await page.goto(url, wait_until="networkidle", timeout=60000)

        html_content = await page.content()
        if "Just a moment..." not in html_content:
            await simulate_human_behavior(page)
            return page, browser

        print(f"Challenge detected. Attempt {attempt + 1}/{MAX_RETRIES}")
        await browser.close()
        await asyncio.sleep(random.uniform(5, 10))

    raise Exception("Failed to bypass challenge after maximum retries")


async def simulate_human_behavior(page):
    page_size = await page.evaluate(
        "() => { return {width: window.innerWidth, height: window.innerHeight} }"
    )
    for _ in range(3):
        x = random.randint(0, page_size["width"])
        y = random.randint(0, page_size["height"])
        await page.mouse.move(x, y)
        await asyncio.sleep(random.uniform(0.5, 1.5))
    await page.mouse.down()
    await page.mouse.move(x + 100, y + 100)
    await page.mouse.up()
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2);")
    await asyncio.sleep(random.uniform(1, 3))
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
    await asyncio.sleep(random.uniform(1, 3))


async def extract_job_info(page, html_content):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, "html.parser")
    job_cards = soup.find_all("div", class_="cardOutline")

    jobs = []
    for card in job_cards:
        title_elem = card.find("h2", class_="jobTitle")
        company_elem = card.find("span", {"data-testid": "company-name"})
        location_elem = card.find("div", {"data-testid": "text-location"})
        link_elem = card.find("a", class_="jcs-JobTitle")

        if title_elem and company_elem and location_elem and link_elem:
            title = title_elem.text.strip()
            company = company_elem.text.strip()
            location = location_elem.text.strip()
            link = "https://www.indeed.com" + link_elem["href"]
            job_id = link_elem.get("data-jk", "N/A")

            # Click on the job card itself to open the description
            print(f"Clicking on job: {title} at {company}")
            await card.click()
            await page.wait_for_load_state("networkidle")
            await page.wait_for_selector("#jobDescriptionText")

            # Extract the job description
            description_elem = await page.query_selector("#jobDescriptionText")
            description_html = await description_elem.inner_html()
            description_text = await description_elem.inner_text()

            # Extract company link
            company_link = ""
            company_link_elem = await page.query_selector("a#companyLink")
            if company_link_elem:
                company_link = await company_link_elem.get_attribute("href")

            jobs.append(
                {
                    "id": job_id,
                    "title": title,
                    "company": company,
                    "location": location,
                    "link": link,
                    "company_link": company_link,
                    "description_html": description_html,
                    "description_text": description_text,
                }
            )

    # Print job details with truncated description
    for job in jobs:
        description_preview = (
            " ".join(job["description_html"].split()[:100]) + "..."
            if job["description_html"]
            else "No description available"
        )
        print(f"Title: {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Location: {job['location']}")
        print(f"Link: {job['link']}")
        print(f"Company Link: {job['company_link']}")
        print(f"Description Preview: {description_preview}")
        print("---")

    return jobs


async def get_next_page_url(page):
    next_button = await page.query_selector('a[data-testid="pagination-page-next"]')
    if next_button:
        return await next_button.get_attribute("href")
    return None
