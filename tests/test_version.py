import toml

import citation_docket


def test_version():
    assert (
        toml.load("pyproject.toml")["tool"]["poetry"]["version"]
        == citation_docket.__version__
    )
