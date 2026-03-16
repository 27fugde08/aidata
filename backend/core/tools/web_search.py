import httpx
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from typing import List, Dict, Any, Optional
import asyncio

class WebSearch:
    """
    Search and retrieve information from the internet.
    Supports DuckDuckGo (free) and basic scraping.
    """
    def __init__(self, max_results: int = 5):
        self.max_results = max_results
        self.ddgs = DDGS()

    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Performs a search and returns snippets and URLs."""
        try:
            # Use DuckDuckGo Search
            results = list(self.ddgs.text(query, max_results=self.max_results))
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")
                }
                for r in results
            ]
        except Exception as e:
            print(f"Search Error: {e}")
            return []

    async def read_page(self, url: str) -> str:
        """Retrieves and cleans the text from a URL."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, follow_redirects=True)
                if response.status_code != 200:
                    return f"Error: Status code {response.status_code}"
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.extract()
                
                # Get text and clean up
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                return text[:10000] # Cap at 10k chars
        except Exception as e:
            return f"Error reading page: {e}"

    async def deep_search(self, query: str) -> str:
        """Search and read the first result's content."""
        results = await self.search(query)
        if not results:
            return "No results found."
        
        first_url = results[0]["url"]
        content = await self.read_page(first_url)
        return f"SOURCE: {first_url}\n\nCONTENT:\n{content[:2000]}"
