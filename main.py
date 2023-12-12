import os
from typing import Iterator, Optional
from urllib.error import HTTPError
from urllib.request import urlopen

import concurrent.futures
import logging
import json

logger = logging.getLogger(__name__)

INDEX_URL = "https://xkcd.com/info.0.json"


def main(output_dir: str, force: bool = False):
    total = get_total_comics()
    urls = iter_download_urls(total)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for url in urls:
            filename = os.path.basename(url)
            path = os.path.join(output_dir, filename)
            future = executor.submit(download, url=url, path=path, force=force)
            futures.append(future)
        concurrent.futures.wait(futures)


def download(url: str, path: str, force: bool = False):
    if os.path.exists(path) and not force:
        logger.info("Skipping %s", path)
        return

    logger.info("Downloading %s -> %s", url, path)
    try:
        with open(path, "wb") as file:
            file.write(urlopen(url).read())
    except HTTPError as e:
        logger.error("Failed to download %s -> %s - %s", url, path, e)
        return

    logger.info("Downloaded %s -> %s", url, path)


def iter_download_urls(total: Optional[int] = None) -> Iterator[str]:
    def _get_download_url(idx: int) -> str:
        return json.loads(urlopen(f"https://xkcd.com/{idx}/info.0.json").read())["img"]

    total = total or get_total_comics()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for i in reversed(range(1, total + 1)):
            future = executor.submit(_get_download_url, i)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            try:
                yield future.result()
            except HTTPError:
                continue


def get_total_comics() -> int:
    data = json.loads(urlopen(INDEX_URL).read())
    return data["num"]


if __name__ == "__main__":

    def cli():
        import argparse

        logging.basicConfig(level=logging.INFO, format="%(message)s")

        parser = argparse.ArgumentParser(description="Bulk download XKCD comics")
        parser.add_argument(
            "-o", "--output-dir", help="Output directory", required=True
        )
        parser.add_argument("-f", "--force", action="store_true", help="Force download")
        args = parser.parse_args()
        kwargs = vars(args)
        main(**kwargs)

    cli()
