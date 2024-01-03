import dataclasses
import os
import sys
from typing import Any, Iterator, Optional
from urllib.error import HTTPError
from urllib.request import urlopen

import logging
import datetime
import concurrent.futures
import json
import os

logger = logging.getLogger(__name__)

BY = {'title', 'safe_title', 'alt', 'img', 'date', 'num'}
BY_DEFAULT = 'num'


def download_comics(output_dir: str, by: Optional[str] = BY_DEFAULT, force: bool = False):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        total = get_total_comics()
        for n in range(1, total + 1):
            if n == 404:
                continue

            future = executor.submit(download_comic, output_dir=output_dir, by=by, n=n, force=force)
            futures.append(future)
            
        for future in concurrent.futures.as_completed(futures):
            future.result()


def download_comic(output_dir: str, n: int, force: bool = False, by: Optional[str] = BY_DEFAULT):
    comic = get_comic(n)
    if not comic:
        return
    
    url = comic['img']
    path = get_output_path(output_dir=output_dir, comic=comic, by=by)

    os.makedirs(output_dir, exist_ok=True)
    if not os.path.exists(path) or force:
        try:
            logger.info("Downloading %s -> %s", url, path)
            with open(path, "wb") as file:
                file.write(urlopen(url).read())
        except HTTPError as e:
            if e.code == 404:
                return
            else:
                logger.warning("Failed to download %s -> %s - %s", url, path, e)
    else:
        logger.debug("Skipping %s -> %s", url, path)
        
    
def get_output_path(output_dir: str, comic: dict, by: Optional[str] = BY_DEFAULT) -> str:
    filename = get_output_filename(comic, by=by)
    return os.path.join(output_dir, filename)


def get_output_filename(comic: dict, by: Optional[str] = BY_DEFAULT) -> str:
    path = comic['img']
    ext = os.path.splitext(path)[1]

    if by:
        by = by.lower()
        by = by.replace('-', '_')

        value = comic[by]
        if isinstance(value, str):
            value = sanitize_filename(value)

        filename = f"{value}{ext}"
    else:
        n = comic['num']
        filename = f'{comic[n]}{ext}'
    return filename


def sanitize_filename(filename: str) -> str:
    for t in ['\'', '"', ' ', '\t', '\n']:
        filename = filename.replace(t, '')
    
    if '/' in filename:
        filename = filename.replace('/', '-')
    return filename


def iter_comics() -> Iterator[dict]:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        total = get_total_comics()
        for n in range(1, total + 1):
            future = executor.submit(get_comic, n)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            comic = future.result()
            if comic:
                yield comic


def get_comic(n: Optional[int] = None) -> Optional[dict]:
    n = n or get_total_comics()
    try:
        meta = json.loads(urlopen(f"https://xkcd.com/{n}/info.0.json").read())
    except HTTPError as e:
        if e.code == 404:
            return None
        raise HTTPError(f"Failed to lookup comic #{n}") from e
    return parse_comic(meta)


def parse_comic(meta: dict) -> dict:
    year = int(meta["year"])
    month = int(meta["month"])
    day = int(meta["day"])
    meta.update({
        'year': year,
        'month': month,
        'day': day,
        'date': datetime.date(year=year, month=month, day=day),
    })
    return meta


def get_total_comics() -> int:
    return json.loads(urlopen("https://xkcd.com/info.0.json").read())['num']


if __name__ == "__main__":
    from json import JSONEncoder

    class JSONEncoder(JSONEncoder):
        def default(self, o):
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            elif isinstance(o, datetime.datetime):
                return o.date().isoformat()
            elif isinstance(o, datetime.date):
                return o.isoformat()
            else:
                return super().default(o)


    def main(output_dir: Optional[str], by: Optional[str], n: Optional[int], force: bool):
        if n:
            if output_dir:
                download_comic(output_dir=output_dir, by=by, n=n, force=force)
            else:
                comic = get_comic(n)
                if comic:
                    if by:
                        print(comic[by])
                    else:
                        print_value(comic)
                else:
                    sys.exit(1)
        else:
            if output_dir:
                download_comics(output_dir=output_dir, by=by, force=force)
            else:
                for value in iter_comics():
                    if by:
                        value = value[by]
                    print_value(value)


    def print_value(value: Any):
        if isinstance(value, datetime.date):
            value = value.isoformat()
        elif isinstance(value, datetime.datetime):
            value = value.date().isoformat()
        elif isinstance(value, dict):
            value = json.dumps(value, indent=2, cls=JSONEncoder)
        print(value)


    def cli():
        import argparse

        logging.basicConfig(level=logging.INFO, format="%(message)s")

        parser = argparse.ArgumentParser(description="Dependency-less XKCD client")
        parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
        parser.add_argument('--output-dir', help='Download comics to this directory')
        parser.add_argument('--force', action='store_true', help='Force download')
        parser.add_argument('-n', '-num', type=int, help='Lookup a comic')
        parser.add_argument('-k', '--by', dest='by', choices=BY, help='Key to use when naming downloaded files')
        args = parser.parse_args()
        kwargs = vars(args)
        if kwargs.pop("verbose"):
            logging.getLogger().setLevel(logging.DEBUG)
        
        main(**kwargs)
    

    cli()
