import argparse

import requests


def summarize(args: argparse.Namespace) -> None:
    response = requests.post(
        "http://0.0.0.0:8760/summarize",
        json={
            "token": "test",
            "type": "test",
            "event": {"text": args.arxiv_id_or_url, "type": "app_mention"},
        },
    )
    print(response.text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--arxiv_id_or_url",
        help="The arXiv ID or URL of the paper to be summarized.",
    )

    args = parser.parse_args()

    if args.mode == "summarize":
        summarize(args)
