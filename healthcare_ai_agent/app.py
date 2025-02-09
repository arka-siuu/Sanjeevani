import os
import sys
import psutil
import asyncio
import re
import requests
from bs4 import BeautifulSoup
from typing import List

# Gemini API Endpoint
GEMINI_API_KEY = "AIzaSyBxmj0zGRP-ndq2VKHjvh1q-XW3_Lrliq0"  # Replace with your Gemini API key
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"

__location__ = os.path.dirname(os.path.abspath(__file__))
__output__ = os.path.join(__location__, "output")

# Append parent directory to system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)


async def fetch_page_content(url: str) -> str:
    """Fetch the content of a webpage using REST (requests)."""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""


async def crawl_parallel(urls: List[str], max_concurrent: int = 3):
    """Crawl URLs in parallel and store results."""
    print("\n=== Parallel Crawling with REST ===")

    peak_memory = 0
    process = psutil.Process(os.getpid())

    def log_memory(prefix: str = ""):
        """Monitor and log memory usage."""
        nonlocal peak_memory
        current_mem = process.memory_info().rss  # in bytes
        if current_mem > peak_memory:
            peak_memory = current_mem
        print(f"{prefix} Current Memory: {current_mem // (1024 * 1024)} MB, Peak: {peak_memory // (1024 * 1024)} MB")

    messages = []
    url_pattern = re.compile(r'https?://\S+|www\.\S+')

    success_count = 0
    fail_count = 0

    for i in range(0, len(urls), max_concurrent):
        batch = urls[i: i + max_concurrent]
        tasks = [fetch_page_content(url) for url in batch]

        log_memory(prefix=f"Before batch {i // max_concurrent + 1}: ")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        log_memory(prefix=f"After batch {i // max_concurrent + 1}: ")

        for url, result in zip(batch, results):
            if isinstance(result, Exception) or not result:
                print(f"Failed to crawl {url}")
                fail_count += 1
            else:
                success_count += 1
                cleaned_content = url_pattern.sub("", result)
                messages.append({"source": url, "content": cleaned_content})

    print(f"\nSummary:\n  - Successfully crawled: {success_count}\n  - Failed: {fail_count}\n")

    return messages


async def process_with_gemini(messages: List[dict]):
    """Process scraped messages using Gemini REST API."""
    llm_knowledge = []

    for message in messages:
        data = {
            "contents": [{"parts": [{"text": message["content"]}]}]
        }
        params = {"key": GEMINI_API_KEY}

        try:
            response = requests.post(GEMINI_API_URL, json=data, params=params)
            response.raise_for_status()
            gemini_response = response.json()

            if "candidates" in gemini_response and gemini_response["candidates"]:
                processed_text = gemini_response["candidates"][0]["content"]["parts"][0]["text"]
            else:
                processed_text = "No meaningful response from Gemini."

            llm_knowledge.append({
                "source": message["source"],
                "knowledge": processed_text
            })

        except requests.exceptions.RequestException as e:
            print(f"Error processing with Gemini: {e}")

    return llm_knowledge


async def answer_user_query(user_query: str, knowledge_base: List[dict]):
    """Finds the best solution for a user's query from scraped knowledge using Gemini."""

    relevant_info = "\n".join([f"{entry['source']}:\n{entry['knowledge']}" for entry in knowledge_base])

    prompt = f"""
    The user has asked: "{user_query}"

    Below is the knowledge base extracted from trusted sources:
    {relevant_info}

    Please provide a personalized response to the user's query using the most relevant information.
    """

    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    params = {"key": GEMINI_API_KEY}

    try:
        response = requests.post(GEMINI_API_URL, json=data, params=params)
        response.raise_for_status()
        gemini_response = response.json()

        if "candidates" in gemini_response and gemini_response["candidates"]:
            answer = gemini_response["candidates"][0]["content"]["parts"][0]["text"]
        else:
            answer = "I'm sorry, but I couldn't find a suitable answer."

        return answer

    except requests.exceptions.RequestException as e:
        print(f"Error fetching personalized solution: {e}")
        return "There was an error processing your request."


async def main():
    urls = [
        "https://mohfw.gov.in/",
        "https://www.india.gov.in/topics/social-development/women",
        "https://wcd.gov.in/directory",
    ]

    if urls:
        print(f"Found {len(urls)} URLs to crawl")
        messages = await crawl_parallel(urls, max_concurrent=10)

        llm_knowledge = await process_with_gemini(messages)

        print("\nLLM Knowledge Processed. Now ready to answer user queries!")

        # Take user query
        user_query = input("\nEnter your question: ")
        personalized_response = await answer_user_query(user_query, llm_knowledge)

        print("\n=== Personalized Solution ===")
        print(personalized_response)

        return personalized_response
    else:
        print("No URLs found to crawl")
        return []


if __name__ == "__main__":
    asyncio.run(main())
