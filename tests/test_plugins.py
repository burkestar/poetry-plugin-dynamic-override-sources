from pathlib import Path

from poetry.config.config import Config
from poetry.factory import Factory
from poetry.poetry import Poetry

from poetry_plugin_dynamic_override_sources.plugins import (
    DynamicOverrideSourcesPlugin,
    parse_environment_variables,
)


def test_parse_environment_variables(monkeypatch):
    monkeypatch.setenv('POETRY_SOURCE_FOO_URL', 'https://foo.example.com/')
    monkeypatch.setenv('POETRY_REPOSITORIES_FOO_URL', 'should-not-be-used')
    monkeypatch.setenv('PIP_INDEX_URL', 'https://global.pip.ndx')

    source_urls = parse_environment_variables()
    assert source_urls == {
        'foo': 'https://foo.example.com/',
        'PyPI': 'https://global.pip.ndx'
    }


def test_dynamic_override_sources_plugin_without_env_vars_set(poetry, io):
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


def test_dynamic_override_sources_plugin_with_env_vars_set(io, monkeypatch):
    proxy_source_url = 'https://some.proxy/'
    monkeypatch.setenv('POETRY_SOURCE_PRIVATE_SOURCE_URL', proxy_source_url)

    poetry = Factory().create_poetry(
        Path(__file__).parent / "fixtures" / "simple_project",
        io=io
    )
    poetry.set_config(Config())

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

