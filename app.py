import os
import re
from typing import Dict

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, validator

from src.pdf_summarization import APIInterface

load_dotenv()


class SummarizeRequest(BaseModel):
    """
    A class to represent the request of the summarize API,
    from Slack Events API.
    """

    token: str
    type: str
    event: Dict

    @validator("event")
    def event_text_must_contain_arxiv_id(cls, v: Dict) -> Dict:
        """
        Validate the event text to contain arXiv ID.

        Parameters
        ----------
        v : Dict
            The event dictionary.

        Returns
        -------
        Dict
            The event dictionary if the text contains arXiv ID.

        Raises
        ------
        ValueError
            If the text does not contain arXiv ID.
        """
        # check if the text contains arXiv ID (e.g. 2101.00001)
        if not re.search(r"\d{4}\.\d{5}", v["text"]):
            raise ValueError("The text must contain arXiv ID.")

        return v

    @validator("event")
    def event_must_be_app_mention(cls, v: Dict) -> Dict:
        """
        Validate the event to be app_mention.

        Parameters
        ----------
        v : Dict
            The event dictionary.

        Returns
        -------
        v : Dict
            The event dictionary if the event is app_mention.

        Raises
        ------
        ValueError
            If the event is not app_mention.
        """
        # check if the event is app_mention
        if v["type"] != "app_mention":
            raise ValueError("The event must be app_mention.")

        return v

    @validator("event")
    def event_client_msg_id_is_unique(cls, v: Dict) -> Dict:
        """
        Validate the client_msg_id to be unique.
        If the client_msg_id is unique, save it to the ts.log file.
        If deplicated, raise ValueError.

        Parameters
        ----------
        v : Dict
            The event dictionary.

        Returns
        -------
        v : Dict
            The event dictionary if the client_msg_id is unique.

        Raises
        ------
        ValueError
            If the client_msg_id is deplicated.
        """
        # check if the client_msd_id is deplicated
        if os.path.exists("msg_id.log"):
            with open("msg_id.log", "r") as f:
                if v["client_msg_id"] in [ts.strip() for ts in f.readlines()]:
                    raise ValueError("The event arxiv_id is deplicated.")

        # save the event arxiv_id to ts.log
        with open("msg_id.log", "a") as f:
            f.write(f"{v['client_msg_id']}\n")

        return v


class SummarizerAPI:
    """
    A class to create and run the Summarizer API using FastAPI.

    Attributes
    ----------
    app : FastAPI
        The FastAPI application instance.
    api_interface : APIInterface
        The API interface for PDF summarization.
    """

    def __init__(self):
        self.app = FastAPI()
        self.api_interface = APIInterface()

        self.app.add_api_route(
            "/summarize",
            self.summarize,
            methods=["POST"],
            response_class=PlainTextResponse,
        )
        self.app.add_event_handler("startup", self.daily_summary)

    def run(self):
        """
        Run the FastAPI application using uvicorn.
        """
        uvicorn.run(self.app, host="0.0.0.0", port=8760)

    async def summarize(self, payload: SummarizeRequest) -> None:
        """
        Summarize the given arXiv paper.

        Parameters
        ----------
        request : SummarizeRequest
            The request object containing the arXiv ID or URL of the paper to be
            summarized.

        Raises
        ------
        Exception
            If the request is invalid.
        """

        try:
            self.api_interface.summarize(
                re.search(r"\d{4}\.\d{5}", payload.event["text"]).group()
            )
        except Exception:
            raise Exception(payload)

    async def daily_summary(self) -> None:
        """
        Get the daily summary of arXiv papers.
        """
        scheduler = AsyncIOScheduler()
        scheduler.add_job(self.api_interface.daily_summary, IntervalTrigger(hours=24))
        scheduler.start()

    async def slack_challenge(self, data: dict) -> str:
        """
        Respond to the Slack challenge request.

        Parameters
        ----------
        data : dict
            The request body of the Slack challenge request.

        Notes
        -----
        This method is only used at the first handshake with Slack.
        At that time, Slack sends a challenge request to the API.
        The API must respond with the challenge value in the specific
        request body.

        In the situation, you have to modify the api route of
        summarization like below:

        >>> self.app.add_api_route(
        >>>     "/summarize",
        >>>     self.slack_challenge,
        >>>     methods=["POST"],
        >>>     response_class=PlainTextResponse,
        >>> )
        """
        return data["challenge"]


if __name__ == "__main__":
    api = SummarizerAPI()
    api.run()
