import dataclasses
import itertools
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


@dataclasses.dataclass()
class Client:
    force: bool = False

    def iter_comics(self, limit: Optional[int] = None) -> Iterator[dict]:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            total = self.get_total_comics()
            for n in itertools.islice(range(1, total + 1), limit):
                future = executor.submit(self.get_comic, n)
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                comic = future.result()
                if comic:
                    yield comic

    def get_comic(self, num: Optional[int] = None) -> Optional[dict]:
        num = num or self.get_total_comics()
        try:
            meta = json.loads(urlopen(f"https://xkcd.com/{num}/info.0.json").read())
        except HTTPError as e:
            if e.code == 404:
                return None
            raise HTTPError(f"Failed to lookup comic #{num}") from e
        return parse_comic_meta(meta)
    
    def latest(self) -> dict:
        return self.get_latest_comic()
    
    def get_latest_comic(self) -> dict:
        return self.get_comic()

    def get_total_comics(self) -> int:
        return json.loads(urlopen("https://xkcd.com/info.0.json").read())['num']

    def download_comics(self, output_dir: Optional[str] = None, limit: Optional[int] = None):
        output_dir = output_dir or os.getcwd()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for comic in self.iter_comics(limit=limit):
                future = executor.submit(self.download_comic, output_dir=output_dir, num=comic['num'])
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                future.result()

    def download_comic(self, output_dir: str, num: Optional[int] = None):
        comic = self.get_comic(num)
        if comic:
            path = self.get_output_path(output_dir, num)
            if not os.path.exists(path) or self.force:
                download_file(comic['img'], path)

    def download_latest(self, output_dir: Optional[str] = None):
        return self.download_comic(output_dir=output_dir)
        
    def get_output_path(self, output_dir: str, num: int) -> str:
        output_dir = output_dir or os.getcwd()
        comic = self.get_comic(num)
        if not comic:
            raise KeyError(f"Comic #{num} not found")

        img = comic['img']
        ext = os.path.splitext(img)[1]
        filename = f'{num}{ext}'
        return os.path.join(output_dir, filename)

    def __iter__(self):
        return self.iter_comics()


def parse_comic_meta(meta: dict) -> dict:
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


def download_file(url: str, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        logger.info("Downloading %s -> %s", url, path)
        with open(path, "wb") as file:
            file.write(urlopen(url).read())
    except HTTPError as e:
        if e.code == 404:
            return
        else:
            logger.warning("Failed to download %s -> %s - %s", url, path, e)


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

    def main(output_dir: Optional[str], num: Optional[int], force: bool, download: bool, sparse_output: bool, latest: bool, limit: Optional[int]):
        client = Client(force=force)

        num = num if num else (client.get_total_comics() if latest else None)
        output_dir = os.getcwd() if (download and output_dir is None) else output_dir
        if output_dir:
            if num:
                client.download_comic(output_dir=output_dir, num=num)
            else:
                client.download_comics(output_dir=output_dir, limit=limit)
        else:
            if num:
                comic = client.get_comic(num)
                if comic:
                    print_value(comic, sparse_output=sparse_output)
                else:
                    sys.exit(1)
            else:
                for value in client.iter_comics(limit=limit):
                    print_value(value, sparse_output=sparse_output)
                

    def print_value(value: Any, sparse_output: bool):
        if isinstance(value, datetime.date):
            value = value.isoformat()
        elif isinstance(value, datetime.datetime):
            value = value.date().isoformat()
        elif isinstance(value, dict):
            if sparse_output:
                value = {k: v for k, v in value.items() if v}
            value = json.dumps(value, cls=JSONEncoder)
        print(value)


    def cli():
        import argparse

        logging.basicConfig(level=logging.INFO, format="%(message)s")

        parser = argparse.ArgumentParser(description="Dependency-less XKCD client")
        parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
        parser.add_argument('-o', '--output-dir', dest='output_dir', help='If provided, download comics to this directory')
        parser.add_argument('-f', '--force', action='store_true', help='Force re-download')
        parser.add_argument('-n', '--num', type=int, help='Comic # (e.g. 1234)')
        parser.add_argument('--latest', action='store_true', help='Get latest comic')
        parser.add_argument('--download', action='store_true', help='Download the comic')
        parser.add_argument('--sparse-output', action='store_true', help='Drop empty JSON fields when listing comic metadata')
        parser.add_argument('--limit', type=int, help='Limit number of comics to download')

        args = parser.parse_args()
        kwargs = vars(args)
        if kwargs.pop("verbose"):
            logging.getLogger().setLevel(logging.DEBUG)
        
        main(**kwargs)
    
    cli()
