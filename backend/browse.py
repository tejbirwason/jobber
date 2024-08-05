from common import app
from modal import Image
from playwright.async_api import async_playwright


@app.function(
    image=Image.debian_slim(python_version="3.10").run_commands(
        "apt-get update",
        "apt-get install -y software-properties-common",
        "apt-add-repository non-free",
        "apt-add-repository contrib",
        "pip install playwright==1.44.0",
        "playwright install-deps chromium",
        "playwright install chromium",
    ),
    timeout=300,
)
async def search_google(term: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        # Navigate directly to Google search results page
        await page.goto(f"https://www.google.com/search?q={term}")

        # Wait for results to load
        await page.wait_for_selector("div#search")

        # Extract search results
        results = await page.evaluate(
            """
            () => {
                const elements = document.querySelectorAll('div.g');
                return Array.from(elements).map(el => {
                    const titleEl = el.querySelector('h3');
                    const linkEl = el.querySelector('a');
                    return {
                        title: titleEl ? titleEl.textContent : '',
                        url: linkEl ? linkEl.href : ''
                    };
                });
            }
        """
        )

        # Print results
        print(f"Search results for '{term}':")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")

        # Extract text from top 3 results
        text_results = []
        for i, result in enumerate(results[:3], 1):
            try:
                print(f"Parsing result {i}: {result['title']}")
                page = await browser.new_page()
                print(f"Navigating to {result['url']}")
                await page.goto(result["url"], wait_until="networkidle")

                # Extract visible text
                print("Extracting visible text")
                text = await page.evaluate("() => document.body.innerText")

                print(f"Extracted {len(text)} characters of text")
                text_results.append({"title": result["title"], "url": result["url"], "text": text})

                await page.close()
                print(f"Finished parsing result {i}")
            except Exception as e:
                print(f"Error extracting text from {result['url']}: {str(e)}")

        await browser.close()
        print(f"Extracted text from {len(text_results)} results")

        # Print extracted text results
        print("\nExtracted text from top 3 results:")
        for i, result in enumerate(text_results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Text (first 200 characters): {result['text']}...")

        return results


# @web_endpoint()
# def search_endpoint(term: str):
#     results = search_google.remote(term)
#     return {"results": results}


@app.local_entrypoint()
def main():
    search_google.remote("hyertek")
