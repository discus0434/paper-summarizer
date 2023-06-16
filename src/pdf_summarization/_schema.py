from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ArxivInfo:
    """
    A dataclass that contains the title,abstract and path of an arXiv
    paper.
    """

    title: str
    abstract: str
    path: Path


@dataclass(frozen=True)
class SlackMessageData:
    """
    A class to represent the data of a Slack message.

    Attributes
    ----------
    title : str
        The title of the paper.
    url : str
        The URL of the paper.
    summary : str
        The summary of the paper.
    """

    title: str
    url: str
    summary: str
