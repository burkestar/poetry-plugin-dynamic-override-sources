from pathlib import Path

import pytest
from cleo.io.buffered_io import BufferedIO
from cleo.io.io import IO
from poetry.config.config import Config
from poetry.core.packages.package import Package
from poetry.factory import Factory
from poetry.poetry import Poetry
from poetry.repositories.repository import Repository
from poetry.repositories.repository_pool import RepositoryPool


@pytest.fixture()
def config() -> Config:
    return Config()


@pytest.fixture()
def io() -> BufferedIO:
    return BufferedIO()


@pytest.fixture()
def poetry(config: Config, io: IO) -> Poetry:
    poetry = Factory().create_poetry(
        Path(__file__).parent / "fixtures" / "simple_project",
        io=io
    )
    poetry.set_config(config)

    # pool = RepositoryPool()
    # repository = Repository("repo")
    # repository.add_package(Package("foo", "1.0.0"))
    # pool.add_repository(repository)
    # poetry.set_pool(pool)

    return poetry
