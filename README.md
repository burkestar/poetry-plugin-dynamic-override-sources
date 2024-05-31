# poetry-plugin-dynamic-override-sources

## Description

*poetry-plugin-dynamic-override-sources* is a [plugin](https://python-poetry.org/docs/master/plugins/)
for [poetry](https://python-poetry.org/) package manager in python.

With pip, you can override the package index URL using [configuration files](https://pip.pypa.io/en/stable/topics/configuration/)
or environment variables such as:

- `PIP_INDEX_URL`
- `PIP_PROXY`

However, with poetry there is no such option.  The pyproject.toml project configuration specifies one or more
[sources](https://python-poetry.org/docs/repositories/#package-sources) that are to be used for resolving packages from the artifact storage.

## Usage

### Installation

See [plugin installation instructions](https://python-poetry.org/docs/plugins#using-plugins).

```bash
$POETRY_HOME/bin/pip install --user git+https://github.com/burkestar/poetry-plugin-dynamic-override-sources
```


## See also

- [poetry-plugin-use-pip-global-index-url](https://github.com/BaxHugh/poetry-plugin-use-pip-global-index-url) - plugin that this was forked from
- [poetry-plugin-pypi-mirror](https://github.com/arcesium/poetry-plugin-pypi-mirror) - upstream plugin that inspired `poetry-plugin-use-pip-global-index-url`.
- [python-poetry/poetry#1632](https://github.com/python-poetry/poetry/issues/1632) - poetry feature request to add support for global repository URL replacement
