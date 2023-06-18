from ._arxiv import Arxiv
from ._id_retriever import IDRetriever
from ._ocr_model import OCRModel
from ._post_to_slack import post_to_slack
from ._schema import SlackMessageData
from ._summarizer import Summarizer


class APIInterface:
    """
    A class to interact with the API for downloading, extracting text,
    and summarizing research papers.

    Attributes
    ----------
    ocr_model : OCRModel
        The OCRModel instance, which uses the PadddleOCR.
    summarizer : Summarizer
        The Summarizer instance, which uses the OpenAI API.
    """

    def __init__(self, model: str = "gpt-3.5-turbo-16k-0613", max_length: int = 16000):
        """
        Initialize the APIInterface with OCRModel and Summarizer
        instances.

        Parameters
        ----------
        model : str, optional
            The OpenAI model to be used for summarization,
            by default "gpt-3.5-turbo-16k-0613"
        max_length : int, optional
            The maximum length of the text to be summarized,
            by default 16000
        """
        self.ocr_model = OCRModel(max_length=max_length)
        self.summarizer = Summarizer(model=model)

    def summarize(self, arxiv_id_or_url: str) -> None:
        """
        Summarize the text of a research paper given its arXiv ID or
        URL.
        Then, post summarized text of the research paper.

        Parameters
        ----------
        arxiv_id_or_url : str
            The arXiv ID or URL of the research paper.
        """
        # 1. Download the paper from arXiv
        print("Downloading the paper...")
        arxiv_info = Arxiv.download(arxiv_id_or_url)

        # 2. Extract text from the paper
        print("Extracting text from the paper...")
        text = self.ocr_model.extract_text(arxiv_info.path) or arxiv_info.abstract

        # 3. Summarize the text
        print("Summarizing the text...")
        summary = self.summarizer.summarize(text)

        # 4. Post the summary to Slack
        post_to_slack(
            [
                SlackMessageData(
                    title=arxiv_info.title,
                    url=f"https://arxiv.org/abs/{arxiv_id_or_url}",
                    summary=summary,
                )
            ]
        )

    def daily_summary(self) -> None:
        """
        Retrieve and summarize daily research papers from arXiv.
        Then, post concatenated text of the summarized research 
        papers to slack.
        """
        # 1. Retrieve arXiv IDs
        arxiv_ids = IDRetriever.retrieve_from_hf()

        # 2. Summarize each paper and concatenate them
        summaries = []
        for arxiv_id in arxiv_ids:
            arxiv_info = Arxiv.download(arxiv_id)
            summary = self.summarizer.summarize(
                self.ocr_model.extract_text(arxiv_info.path) or arxiv_info.abstract
            )

            summaries.append(
                SlackMessageData(
                    title=arxiv_info.title,
                    url=f"https://arxiv.org/abs/{arxiv_id}",
                    summary=summary,
                )
            )

        # 3. Post to Slack
        post_to_slack(summaries)
