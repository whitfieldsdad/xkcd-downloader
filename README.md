# Yet another XKCD downloader

This is a simple, dependendency-free Python script for downloading every XKCD comic.

![XKCD #350](network.png)

## Features

- List information about comics in JSON format
- Download the latest comic or historical comits
- Downloads can be forced with `--force`
- Multithreaded downloads

## Usage

### Command line interface

#### Latest comic

To list information about the latest comic:

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

To download the latest comic to the current directory:

```bash
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 - --latest --download
```

To download the latest comic to a specific directory:

```bash
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 - --latest -o xkcd/
```

#### Historical comics

To list information about every comic:

```bash
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 -
```

For example, to list all alt texts:

```bash
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 - | jq -r '.alt' | sort | uniq
```

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

To list all titles:

```bash
python3 xkcd.py | jq -r '.title' | sort | uniq
```

To list all alt texts:

```bash
python3 xkcd.py | jq -r '.alt' | sort | uniq
```

To list all download URLs:

```bash
python3 xkcd.py | jq -r '.img' | sort | uniq
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
