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

CACHE_DIR = os.path.join(tempfile.gettempdir(), "xkcd")
URL_CACHE_PATH = os.path.join(CACHE_DIR, "urls.json")


def main(output_dir: str, force: bool = False):
    pending = {}
    urls = list(iter_download_urls())
    for url in urls:
        path = os.path.join(output_dir, os.path.basename(url))
        if not os.path.exists(path) or force:
            pending[url] = path

    if pending:        
        logger.debug("Downloading %d comics", len(pending))
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


def iter_download_urls() -> Iterator[str]:
    def resolve_download_url(url: str) -> str:
        return json.loads(urlopen(url).read())["img"]

    total = get_total_comics()
    cache = read_url_cache()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {}
        for i in range(1, total + 1):
            api_url = f"https://xkcd.com/{i}/info.0.json"
            img_url = cache.get(api_url)
            if img_url:
                cache[api_url] = img_url
                yield img_url
            else:
                future = executor.submit(resolve_download_url, api_url)
                futures[future] = api_url
        
        if futures:
            for future in concurrent.futures.as_completed(futures):
                api_url = futures[future]
                try:
                    img_url = future.result()
                except HTTPError as e:
                    if e.code == 404:
                        continue
                    raise
                else:
                    cache[api_url] = img_url
                    yield img_url

    update_url_cache(cache)


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
        args = parser.parse_args()
        kwargs = vars(args)
        if kwargs.pop("verbose"):
            logging.getLogger().setLevel(logging.DEBUG)

        main(**kwargs)

    cli()
