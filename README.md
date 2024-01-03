# Yet another XKCD downloader

This is a simple, dependendency-free Python script for downloading every XKCD comic.

## Features

- List information about comics in JSON format
- Download the latest comic or historical comits
- Downloads can be forced with `--force`

## Usage

### Latest comic

To list information about the latest comic:

```bash
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 - --latest
```

To download the latest comic to the current directory:

```bash
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 - --latest --download
```

To download the latest comic to a specific directory:

```bash
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 - --latest -o xkcd/
```

### Historical comics

To list information about every comic:

```bash
curl https://raw.githubusercontent.com/whitfieldsdad/xkcd-downloader/main/xkcd.py -s | python3 -
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
