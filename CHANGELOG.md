# Changelog

## 0.0.6

- Only override repositories of type HTTPRepository which make web requests.
- Log to the console that the plugin is overriding repository urls so users can diagnose issues.

## 0.0.5

- Improve packaging to include link to repo and changelog

## 0.0.4

- Update README about installing using `poetry self add`, and how to publish to PyPI.

## 0.0.3

- Supports environment variable `PIP_INDEX_URL` to override the url for all sources
- Supports environment variables like `POETRY_SOURCE_SOME_REPO_URL` to override the url for `some-repo` source.
- Adds special handing for `POETRY_SOURCE_PYPI_URL` for `PyPI` repo.

## 0.0.2

- Not yet functional and barely tested
