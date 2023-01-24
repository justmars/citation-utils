import citation_date
import toml


def test_version():
    assert (
        toml.load("pyproject.toml")["tool"]["poetry"]["version"]
        == citation_date.__version__
    )
