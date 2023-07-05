import os
import re
from pathlib import Path
from typing import List, Union, Tuple
from concurrent.futures import ThreadPoolExecutor

import nltk
import numpy as np
from nltk.corpus import words
from paddleocr import PaddleOCR, PPStructure
from pdf2image import convert_from_bytes, convert_from_path
from PIL import Image
from tqdm import tqdm
from transformers import GPT2Tokenizer


class OCRModel:
    """
    The OCRModel class that extracts text from a PDF file.
    PPStructure is used to extract the layout of the PDF file,
    and PaddleOCR is used to extract the text from the PDF file.

    Attributes
    ----------
    max_length : int
        The maximum token length of the text to handle with OpenAI API.
    layout_model : PPStructure
        The layout model.
    ocr_model : PaddleOCR
        The OCR model.
    tokenizer : GPT2Tokenizer
        The GPT2Tokenizer instance to calculate the token length.
    """

    def __init__(self, max_length: int = 16000):
        """
        Initialize the OCRModel with layout and OCR models, and download
        the set of English words.

        Parameters
        ----------
        max_length : int
            The maximum length of the text to be extracted.
        """
        self.max_length = max_length
        self.layout_model = PPStructure(table=False, ocr=False, lang="en")
        self.ocr_model = PaddleOCR(ocr=True, lang="en", ocr_version="PP-OCRv3")
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

        # Download the set of English words
        nltk.download("words")

    def extract_text(self, pdf_file: Union[Path, bytes]) -> Union[str, None]:
        """
        Extract text from a PDF file in parallel.
        If the extracted text is too long, return None instead.

        Parameters
        ----------
        pdf_file : Union[Path, bytes]
            The PDF file to extract text from, either as a Path or bytes.

        Returns
        -------
        str
            The extracted text.
            If the extracted text is too long, return None instead.
        """
        texts = []
        pil_images = self.__convert_pdf_to_pil(pdf_file)
        with ThreadPoolExecutor(max_workers=int(os.getenv("MAX_WORKERS", 1))) as executor:
            results = executor.map(self.__extract_text_from_one_page, pil_images)
            for result in tqdm(results, total=len(pil_images)):
                texts.extend(list(result[0]))
                if result[1]:
                    break

        if not self.__is_too_long("\n".join(texts)):
            return "\n".join(texts)
        else:
            return None

    def __extract_text_from_one_page(self, pil_image: Image.Image) -> Tuple[List[str], bool]:
        """
        Extract text from a PIL image of one page.

        Parameters
        ----------
        pil_image : Image.Image
            The PIL image to extract text from.

        Returns
        -------
        List[str]
            The extracted text.
        bool
            Whether the text extraction should be stopped.
        """
        texts = []
        result = self.layout_model(np.array(pil_image, dtype=np.uint8))
        for line in result:
            try:
                if not line["type"] == "title":
                    ocr_results = list(map(lambda x: x[0], self.ocr_model(line["img"])[1]))

                    if len(ocr_results) > 1:
                        text = " ".join(ocr_results)
                        text = re.sub(r"\n|\t|\/|\|", " ", text)

                        if self.__is_unnecessary(text):
                            continue

                        texts.append(text)
                else:
                    try:
                        title = self.ocr_model(line["img"])[1][0][0]
                    except IndexError:
                        continue

                    # if title is "References" or "Reference", stop extracting
                    # because the following text is references and appendices
                    # which are might be unnecessary for our purpose
                    if title.lower() == "references" or title.lower() == "reference":
                        return texts, True
                    texts.append(title)
            except Exception as e:
                print(e)
                continue

        return texts, False

    def __convert_pdf_to_pil(self, pdf_file: Union[Path, bytes]) -> List[Image.Image]:
        """
        Convert a PDF file to a list of PIL images.

        Parameters
        ----------
        pdf_file : Union[Path, bytes]
            The PDF file to convert, either as a Path or bytes.

        Returns
        -------
        List[Image.Image]
            The list of PIL images.
        """
        if isinstance(pdf_file, Path):
            return convert_from_path(pdf_file, dpi=200)
        else:
            return convert_from_bytes(pdf_file, dpi=200)

    def __is_too_long(self, text: str) -> bool:
        """
        Check if a text is too long based on the number of tokens.

        Parameters
        ----------
        text : str
            The text to check.

        Returns
        -------
        bool
            True if the text is too long, False otherwise.
        """
        return len(self.tokenizer(text)["input_ids"]) > self.max_length - 2000

    def __is_unnecessary(self, text: str) -> bool:
        """
        Check if a text is unnecessary based on certain conditions.

        Parameters
        ----------
        text : str
            The text to check.

        Returns
        -------
        bool
            True if the text is unnecessary, False otherwise.
        """
        # if most of the text is numbers, skip
        if len(re.findall(r"\d", text)) / len(text) > 0.3:
            return True

        if (
            text.lower().startswith("figure")
            or text.lower().startswith("igure")
            or text.lower().startswith("table")
        ):
            return True

        # if most of sentences are meaningless, skip
        if self.__is_meaningless(text):
            return True
        return False

    def __is_meaningless(self, text: str) -> bool:
        """
        Check if a text is meaningless based on the proportion of valid English words.

        Parameters
        ----------
        text : str
            The text to check.

        Returns
        -------
        bool
            True if the text is meaningless, False otherwise.
        """
        # Create a set of English words
        word_list = set(words.words())
        # Break the text into words
        words_in_text = text.split()
        # Check if each word is in the English dictionary
        num_valid_words = len(
            [word for word in words_in_text if word.lower() not in word_list]
        )
        return num_valid_words / len(words_in_text) > 0.5
