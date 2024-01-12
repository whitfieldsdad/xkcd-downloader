build:
	poetry build

release: build
	poetry publish

data:
	python3 xkcd.py | jq -c '.' > data/comics.jsonl
	python3 xkcd.py | jq --slurp '.' > data/comics.json
	python3 xkcd.py | jq -r '.alt' | sort > data/alt.txt
	python3 xkcd.py | jq -r '.safe_title' | sort > data/titles.txt
	python3 xkcd.py | jq -r '.img' | sort > data/urls.txt

.PHONY: data