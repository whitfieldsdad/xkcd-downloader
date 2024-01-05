# Yet another XKCD downloader

This is a simple, dependendency-free Python script for downloading every XKCD comic via the author's [API](https://xkcd.com/json.html).

- [tl;dr](#tldr)
- [Features](#features)
- [Usage](#usage)
  - [Command line](#command-line)
    - [Download all comics](#download-all-comics)
    - [Download the latest comic](#download-the-latest-comic)
    - [Get information about the latest comic](#get-information-about-the-latest-comic)
    - [Historical comics](#historical-comics)
  - [Python module](#python-module)
    - [Latest comic](#latest-comic)
    - [Historical comics](#historical-comics-1)
- [Notes](#notes)

## tl;dr

To download every comic to `xkcd/`:

```bash
mkdir -p xkcd
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 - -o xkcd/
```

## Features

- List information about comics in JSONL format
- Download the latest comic or all comics to a directory
- Automatically cache comic metadata to avoid looking up the same information over and over again
- Automatically inject [ISO-8601 dates](https://xkcd.com/1179/) into comic metadata to make it easier to sort and filter comics by date

## Usage

### Command line

The following options are available:

```bash
python3 xkcd.py --help
```

```text
usage: xkcd.py [-h] [-v] [-o OUTPUT_DIR] [-f] [-n NUM] [--latest] [--download] [--sparse-output] [--limit LIMIT]

Dependency-less XKCD client

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Enable debug logging
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        If provided, download comics to this directory
  -f, --force           Force re-download
  -n NUM, --num NUM     Comic # (e.g. 1234)
  --latest              Get latest comic
  --download            Download the comic
  --sparse-output       Drop empty JSON fields when listing comic metadata
  --limit LIMIT         Limit number of comics to download
```

The following commands are equivalent:

```bash
python3 xkcd.py
```

```bash
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 -
```

#### Download all comics

To download all comics to the current directory:

```bash
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 - --download
```

To download all comics to a specific directory:

```bash
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 - -o xkcd/
```

#### Download the latest comic

```bash
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 - --latest --download
```

To download the latest comic to a specific directory:

```bash
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 - --latest -o xkcd/
```

#### Get information about the latest comic

```bash
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 - --latest | jq
```

```json
{
  "month": 1,
  "num": 2875,
  "link": "",
  "year": 2024,
  "news": "",
  "safe_title": "2024",
  "transcript": "",
  "alt": "It wasn't originally constitutionally required, but presidents who served two terms have traditionally followed George Washington's example and gotten false teeth.",
  "img": "https://imgs.xkcd.com/comics/2024.png",
  "title": "2024",
  "day": 1,
  "date": "2024-01-01"
}
```

#### Historical comics

To download all comics to the current directory:

```bash
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 - --download
```

To download all comics to a specific directory:

```bash
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 - -o xkcd/
```

To download a specific comic (e.g. [#1234](https://xkcd.com/1234/)):

```bash
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 - -n 1234 -o .
```

To list information about every comic:

```bash
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 -
```

To list all titles:

```bash
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 - | jq -r '.title' | sort | uniq
```

To list all alt texts:

```bash
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 - | jq -r '.alt' | sort | uniq
```

To list all download URLs:

```bash
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 - | jq -r '.img' | sort | uniq
```

### Python module

#### Latest comic

To list information about the latest comic:

```python
from xkcd import Client

client = Client()
print(client.latest())
```

To download the latest comic to the current directory:

```python
from xkcd import Client

client = Client()
client.download_latest()
```

To download the latest comic to a specific directory:

```python
from xkcd import Client

client = Client()
client.download_latest(output_dir='xkcd/')
```

#### Historical comics

To list information about every comic:

```python
from xkcd import Client

client = Client()
for comic in client.iter_comics():
    print(comic)
```

To download all comics to the current directory:

```python
from xkcd import Client

client = Client()
client.download_comics()

```

To download all comics to a specific directory:

```python
from xkcd import Client

client = Client()
client.download_comics(output_dir='xkcd/')
```

To download a specific comic (e.g. [#1234](https://xkcd.com/1234/)):

```python
from xkcd import Client

client = Client()
client.download_comic(output_dir='xkcd', num=1234)
```

## Notes

1. There is no comic [#404](https://xkcd.com/404/).

![GitHub Copilot knows why](docs/images/404.png)

2. XKCD has a great [API](https://xkcd.com/json.html). You should use it instead of scraping the website.
3. The following information is available for each comic via the API:

```bash
curl https://xkcd.com/614/info.0.json --silent | jq 
```

```json
{
  "month": "7",
  "num": 614,
  "link": "",
  "year": "2009",
  "news": "",
  "safe_title": "Woodpecker",
  "transcript": "[[A man with a beret and a woman are standing on a boardwalk, leaning on a handrail.]]\nMan: A woodpecker!\n<<Pop pop pop>>\nWoman: Yup.\n\n[[The woodpecker is banging its head against a tree.]]\nWoman: He hatched about this time last year.\n<<Pop pop pop pop>>\n\n[[The woman walks away.  The man is still standing at the handrail.]]\n\nMan: ... woodpecker?\nMan: It's your birthday!\n\nMan: Did you know?\n\nMan: Did... did nobody tell you?\n\n[[The man stands, looking.]]\n\n[[The man walks away.]]\n\n[[There is a tree.]]\n\n[[The man approaches the tree with a present in a box, tied up with ribbon.]]\n\n[[The man sets the present down at the base of the tree and looks up.]]\n\n[[The man walks away.]]\n\n[[The present is sitting at the bottom of the tree.]]\n\n[[The woodpecker looks down at the present.]]\n\n[[The woodpecker sits on the present.]]\n\n[[The woodpecker pulls on the ribbon tying the present closed.]]\n\n((full width panel))\n[[The woodpecker is flying, with an electric drill dangling from its feet, held by the cord.]]\n\n{{Title text: If you don't have an extension cord I can get that too.  Because we're friends!  Right?}}",
  "alt": "If you don't have an extension cord I can get that too.  Because we're friends!  Right?",
  "img": "https://imgs.xkcd.com/comics/woodpecker.png",
  "title": "Woodpecker",
  "day": "24"
}
```

4. The above information is lightly modified to make numbers numbers and to include a date in ISO-8601 format:

```json
{
  "month": 7,
  "num": 614,
  "link": "",
  "year": 2009,
  "news": "",
  "safe_title": "Woodpecker",
  "transcript": "[[A man with a beret and a woman are standing on a boardwalk, leaning on a handrail.]]\nMan: A woodpecker!\n<<Pop pop pop>>\nWoman: Yup.\n\n[[The woodpecker is banging its head against a tree.]]\nWoman: He hatched about this time last year.\n<<Pop pop pop pop>>\n\n[[The woman walks away.  The man is still standing at the handrail.]]\n\nMan: ... woodpecker?\nMan: It's your birthday!\n\nMan: Did you know?\n\nMan: Did... did nobody tell you?\n\n[[The man stands, looking.]]\n\n[[The man walks away.]]\n\n[[There is a tree.]]\n\n[[The man approaches the tree with a present in a box, tied up with ribbon.]]\n\n[[The man sets the present down at the base of the tree and looks up.]]\n\n[[The man walks away.]]\n\n[[The present is sitting at the bottom of the tree.]]\n\n[[The woodpecker looks down at the present.]]\n\n[[The woodpecker sits on the present.]]\n\n[[The woodpecker pulls on the ribbon tying the present closed.]]\n\n((full width panel))\n[[The woodpecker is flying, with an electric drill dangling from its feet, held by the cord.]]\n\n{{Title text: If you don't have an extension cord I can get that too.  Because we're friends!  Right?}}",
  "alt": "If you don't have an extension cord I can get that too.  Because we're friends!  Right?",
  "img": "https://imgs.xkcd.com/comics/woodpecker.png",
  "title": "Woodpecker",
  "day": 24,
  "date": "2009-07-24"
}
```