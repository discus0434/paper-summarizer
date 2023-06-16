import re
from datetime import date
from typing import List

import requests
from bs4 import BeautifulSoup


class IDRetriever:
    """
    The IDRetriever class that retrieves arXiv IDs from various sources.
    Currently, it only supports Hugging Face.
    """
    @staticmethod
    def retrieve_from_hf() -> List[str]:
        """
        Retrieve the arXiv IDs of the papers curated by Hugging Face.

        Returns
        -------
        List[str]
            The list of arXiv IDs.
        """
        soup = BeautifulSoup(
            requests.get(
                f"https://huggingface.co/papers?date={date.today().strftime('%Y-%m-%d')}"
            ).text,
            "html.parser",
        )

        arxiv_ids = []
        for article in soup.find_all("article"):
            for a in article.find_all("a"):
                href = a.get("href")
                if re.match(r"^/papers/\d{4}\.\d{5}$", href):
                    arxiv_ids.append(href.split("/")[-1])

        return list(set(arxiv_ids))
