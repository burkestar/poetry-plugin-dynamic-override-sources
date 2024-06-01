import typing as t
from pathlib import Path

import pytest
from cleo.io.buffered_io import BufferedIO
from cleo.io.io import IO
from poetry.config.config import Config
from poetry.factory import Factory
from poetry.poetry import Poetry
from poetry.repositories.repository import Repository

from poetry_plugin_dynamic_override_sources.plugins import (
    DynamicOverrideSourcesPlugin,
    parse_environment_variables,
)


@pytest.fixture()
def config() -> Config:
    return Config()


@pytest.fixture()
def io() -> BufferedIO:
    return BufferedIO()


@pytest.fixture()
def poetry_factory(config: Config, io: IO) -> t.Callable[[], Poetry]:
    def _inner():
        poetry = Factory().create_poetry(
            Path(__file__).parent / "fixtures" / "simple_project",
            io=io
        )
        poetry.set_config(config)
        return poetry

    return _inner


def test_parse_environment_variables(monkeypatch):
    monkeypatch.setenv('POETRY_SOURCE_SOME_REPO_URL', 'https://foo.example.com/')
    monkeypatch.setenv('POETRY_SOURCE_PYPI_URL', 'https://some.other.pypi.org/')
    monkeypatch.setenv('POETRY_REPOSITORIES_FOO_URL', 'should-not-be-used')
    monkeypatch.setenv('PIP_INDEX_URL', 'not-parsed')

    source_urls = parse_environment_variables()
    assert source_urls == {
        'some-repo': 'https://foo.example.com/',
        'PyPI': 'https://some.other.pypi.org/'
    }


def test_dynamic_override_sources_plugin_without_env_vars_set(poetry_factory, io):
    poetry: Poetry = poetry_factory()

    plugin = DynamicOverrideSourcesPlugin()
    plugin.activate(poetry, io)

    project_name = 'simple-project'
    source_name = 'private-source'
    source_url = 'https://some.private.repo/artifacts/'

    # the package was loaded correctly
    assert poetry.package.name == project_name

    # and the package has the expected source definition
    private_source = [source for source in poetry.get_sources() if source.name == source_name][0]
    assert private_source.url == source_url

    # and a repository is created from the package's source
    repo = [repo for repo in poetry.pool.repositories if repo.name == source_name][0]
    # with the original source url (no override was provided) - note the trailing slash is stripped
    assert repo.url == source_url[:-1]


def test_dynamic_override_sources_plugin_with_env_vars_set(poetry_factory, io, monkeypatch):
    proxy_source_url = 'https://some.proxy/'
    monkeypatch.setenv('POETRY_SOURCE_PRIVATE_SOURCE_URL', proxy_source_url)

    poetry: Poetry = poetry_factory()

    plugin = DynamicOverrideSourcesPlugin()
    plugin.activate(poetry, io)

    project_name = 'simple-project'
    source_name = 'private-source'

    # the package was loaded correctly
    assert poetry.package.name == project_name

    # and a repository is created from the package's source
    repo = [repo for repo in poetry.pool.repositories if repo.name == source_name][0]

    # with the repo's url replaced by the proxy override instead (trailing slash is stripped)
    assert repo.url == proxy_source_url[:-1]


def test_dynamic_override_sources_plugin_with_pip_index_url(poetry_factory, io, monkeypatch):
    pip_index_url = 'https://proxy.pypi.org/'
    monkeypatch.setenv('PIP_INDEX_URL', pip_index_url)

    proxy_source_url = 'https://some.proxy/'
    monkeypatch.setenv('POETRY_SOURCE_PRIVATE_SOURCE_URL', proxy_source_url)

    poetry: Poetry = poetry_factory()

    # add an extra repo
    repository = Repository("repo")
    poetry.pool.add_repository(repository)

    plugin = DynamicOverrideSourcesPlugin()
    plugin.activate(poetry, io)

    project_name = 'simple-project'
    source_name = 'private-source'

    # the package was loaded correctly
    assert poetry.package.name == project_name

    # and a repository is created from the package's source
    assert [repo for repo in poetry.pool.repositories if repo.name == source_name]

    # and all repository urls were overridden
    for repo in poetry.pool.repositories:
        assert repo.url == pip_index_url[:-1], repo.url
