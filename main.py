import os
from typing import Iterator, Optional
from urllib.error import HTTPError
from urllib.request import urlopen

import concurrent.futures
import logging
import tempfile
import json
import os

logger = logging.getLogger(__name__)

CACHE_DIR = os.path.join(tempfile.gettempdir(), "4b9e83bf-388d-4696-af5e-9d44786abccb")
URL_CACHE_PATH = os.path.join(CACHE_DIR, "xkcd-download-urls.json")


def main(output_dir: str, start: Optional[int] = None, end: Optional[int] = None, force: bool = False):
    os.makedirs(output_dir, exist_ok=True)
    
    urls = list(iter_download_urls(start=start, end=end))
    logger.info("Found %d comics", len(urls))

    pending = {}
    for url in urls:
        path = os.path.join(output_dir, os.path.basename(url))
        if not os.path.exists(path) or force:
            pending[url] = path
        
    if not pending:
        logger.info("All %d comics have already been downloaded", len(urls))
        return

    logger.info("Downloading %d/%d comics", len(pending), len(urls))
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for url, path in pending.items():
            future = executor.submit(download, url=url, path=path)
            futures.append(future)
        
        for future in concurrent.futures.as_completed(futures):
            future.result()

        logger.debug("Downloaded %d comics", len(futures))
    logger.debug("All %d comics have been downloaded", len(urls))


def download(url: str, path: str):
    logger.debug("Downloading %s -> %s", url, path)
    try:
        with open(path, "wb") as file:
            file.write(urlopen(url).read())
    except HTTPError as e:
        logger.warning("Failed to download %s -> %s - %s", url, path, e)
        return
    else:
        logger.debug("Downloaded %s -> %s", url, path)


def iter_download_urls(start: Optional[int] = None, end: Optional[int] = None) -> Iterator[str]:
    url_cache = read_url_cache()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {}
        for intermediate_url in _iter_intermediate_urls(start=start, end=end):
            if intermediate_url in url_cache:
                yield url_cache[intermediate_url]
            else:
                future = executor.submit(_resolve_intermediate_url, intermediate_url)
                futures[future] = intermediate_url
        
        for future in concurrent.futures.as_completed(futures):
            intermediate_url = futures[future]
            try:
                download_url = future.result()
            except HTTPError as e:
                if e.code == 404:
                    continue
                raise HTTPError(f"Failed to resolve intermediate URL: {intermediate_url}") from e
            else:
                url_cache[intermediate_url] = download_url
                yield download_url

    update_url_cache(url_cache)


def _iter_intermediate_urls(start: Optional[int] = None, end: Optional[int] = None) -> Iterator[str]:
    total = get_total_comics()

    start = start or 1
    end = end or total
    end = min(end, total)

    for i in range(start, end + 1):
        yield f"https://xkcd.com/{i}/info.0.json"


def _resolve_intermediate_url(url: str) -> str:
    return json.loads(urlopen(url).read())["img"]


def get_total_comics() -> int:
    data = json.loads(urlopen("https://xkcd.com/info.0.json").read())
    return data["num"]


def read_url_cache(path: Optional[str] = URL_CACHE_PATH) -> dict:
    try:
         with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.decoder.JSONDecodeError:
        os.unlink(path)
        return {}


def update_url_cache(cache: dict, path: Optional[str] = URL_CACHE_PATH):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    with open(path, "w") as file:
        json.dump(cache, file)


if __name__ == "__main__":
    def cli():
        import argparse

        logging.basicConfig(level=logging.INFO, format="%(message)s")

        parser = argparse.ArgumentParser(description="Bulk download XKCD comics")
        parser.add_argument(
            "-o", "--output-dir", help="Output directory", required=True
        )
        parser.add_argument("-f", "--force", action="store_true", help="Force download")
        parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')
        parser.add_argument('--start', type=int, help='Start comic (e.g. 500)')
        parser.add_argument('--end', type=int, help='End comic (e.g. 1000)')

        args = parser.parse_args()
        kwargs = vars(args)
        if kwargs.pop("verbose"):
            logging.getLogger().setLevel(logging.DEBUG)

        main(**kwargs)

    cli()
