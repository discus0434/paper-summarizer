import os
from pathlib import Path
from typing import Optional

import arxiv

from ._schema import ArxivInfo


class Arxiv:
    """
    A class to download research papers from arXiv.
    """
    @staticmethod
    def download(
        id_or_url: str, save_dir: Optional[Path] = Path("./temp")
    ) -> ArxivInfo:
        """
        Download an arXiv paper given its ID, URL or path and save it to
        a specified directory.

        Parameters
        ----------
        id_or_url : str
            The arXiv paper ID or URL.
        save_dir : Optional[Path], default=Path("./temp")
            The directory where the downloaded paper will be saved.

        Returns
        -------
        ArxivInfo
            The title, abstract and path of the downloaded paper.
        """
        save_dir.mkdir(parents=True, exist_ok=True)

        if id_or_url.startswith("https://arxiv.org/"):
            arxiv_id = id_or_url.split("/")[-1]
        elif os.path.exists(id_or_url):
            return Path(id_or_url)
        else:
            arxiv_id = id_or_url

        info = next(arxiv.Search(id_list=[arxiv_id]).results())
        return ArxivInfo(
            title=info.title,
            abstract=info.summary,
            path=Path(info.download_pdf(save_dir, filename=f"{arxiv_id}.pdf")),
        )
