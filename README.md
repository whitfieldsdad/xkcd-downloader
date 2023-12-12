# Yet another XKCD downloader

This is a simple, dependency-free, multithreaded Python script that you can use to download every [XKCD](https://xkcd.com) comic in a matter of minutes.

It took me about 1.5 minutes to download 2,880 comics (~150 MB of PNG files) and is designed to be idempotent by default - if you run it again, it will only download comics that you don't already have.

## Features

- Multi-threaded downloads
- Ability to force re-download any existing comics with `--force`

## Usage

To download every XKCD comic, simply point the script to a directory where you'd like to save the downloaded comics:

```bash
python3 main.py -o data/
```
