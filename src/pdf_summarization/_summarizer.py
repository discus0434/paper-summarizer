import inspect
import os

import openai


class Summarizer:
    """
    A class to summarize research papers using OpenAI's API.

    Attributes
    ----------
    model : str
        The OpenAI model to be used for summarization.
    """
    def __init__(self, model: str = "gpt-3.5-turbo-16k-0613") -> None:
        """
        Initialize the Summarizer class with an OCRModel instance and set the OpenAI API key.

        Parameters
        ----------
        model : str, optional
            The OpenAI model to be used for summarization,
            by default "gpt-3.5-turbo-16k-0613"
        """
        self.model = model

        openai.organization = os.getenv("OPENAI_ORGANIZATION", "")
        openai.api_key = os.getenv("OPENAI_API_KEY")

    @property
    def __user_prompt(self) -> str:
        """
        Returns a formatted user prompt string.

        Returns
        -------
        str
            The user prompt string.
        """
        return inspect.cleandoc(
            """
            以下の4つの質問について、順を追って詳細に、分かりやすく答えてください。

            1. 既存研究では何ができなかったのか
            2. どのようなアプローチでそれを解決しようとしたか
            3. 結果、何が達成できたのか
            4. 今後の課題は何か
            """
        )

    @property
    def __system_message_format(self) -> str:
        """
        Returns a formatted system message string.

        Returns
        -------
        str
            The system message string.
        """
        return inspect.cleandoc(
            """
            以下のテキストは、ある論文(PDF)をOCRで文章抽出したものです。
            OCRモデルの精度は確約されていないため、文章の一部が抽出されていない可能性があります。
            また、論文の構造によっては、本文以外の部分が抽出されている可能性があります。
            それを踏まえた上で、以下の文章を理解し、ユーザーの質問に答えてください。

            '''
            {text}
            '''
            """
        )

    def summarize(self, text: str) -> str:
        """
        Summarize the given text using OpenAI's language model.

        Parameters
        ----------
        text : str
            The text to be summarized.

        Returns
        -------
        str
            The summarized text.
        """
        response = openai.ChatCompletion.create(
            model=self.model,
            max_tokens=2000,
            messages=[
                {
                    "role": "system",
                    "content": self.__system_message_format.format(text=text),
                },
                {"role": "user", "content": self.__user_prompt},
            ],
        )
        return response["choices"][0]["message"]["content"]
