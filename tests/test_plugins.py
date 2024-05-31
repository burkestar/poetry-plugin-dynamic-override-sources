from poetry_plugin_dynamic_override_sources.plugins import parse_environment_variables


def test_parse_environment_variables(monkeypatch):
    monkeypatch.setenv('POETRY_SOURCE_FOO_URL', 'https://foo.example.com/')
    monkeypatch.setenv('POETRY_REPOSITORIES_FOO_URL', 'should-not-be-used')
    monkeypatch.setenv('PIP_INDEX_URL', 'https://global.pip.ndx')

    source_urls = parse_environment_variables()
    assert source_urls == {
        'FOO': 'https://foo.example.com/',
        'PyPI': 'https://global.pip.ndx'
    }
