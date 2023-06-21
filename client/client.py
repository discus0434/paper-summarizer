import argparse

import requests


def summarize(args: argparse.Namespace) -> None:
    response = requests.post(
        "http://0.0.0.0:8762/summarize",
        json={
            "token": "Jhj5dZrVaK7ZwHHjRyZWjbDl",
            "type": "app_mention",
            "event": {
                "text": args.arxiv_id_or_url,
                "type": "app_mention",
                "client_msg_id": "aaa"
            },
        },
    )
    print(response.text)


def challenge(args: argparse.Namespace) -> None:
    response = requests.post(
        "http://0.0.0.0:8762/summarize",
        json={
            "token": "Jhj5dZrVaK7ZwHHjRyZWjbDl",
            "challenge": "3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P",
            "type": "url_verification"
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
    parser.add_argument(
        "-m",
        "--mode",
    )

    args = parser.parse_args()

    if args.mode == "summarize":
        summarize(args)
    elif args.mode == "challenge":
        challenge(args)
