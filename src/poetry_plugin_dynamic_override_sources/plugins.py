from __future__ import annotations

import os
import re

from cleo.io.io import IO
from poetry.config.config import Config
from poetry.core.constraints.version import Version
from poetry.core.packages.package import Package
from poetry.plugins.plugin import Plugin
from poetry.poetry import Poetry
from poetry.repositories.legacy_repository import LegacyRepository
from poetry.repositories.pypi_repository import PyPiRepository
from poetry.repositories.repository_pool import PrioritizedRepository, Priority

PYPI_SOURCE = 'PyPI'


def parse_environment_variables() -> dict:
    """ Parse environment variables for configuration of source URLs.

    `POETRY_SOURCE_FOO_URL` will override the URL for source `FOO`
    """
    source_urls = {}

    for key, val in os.environ.items():
        match = re.match('^POETRY_SOURCE_(.*)_URL$', key)
        if match:
            source_name = match.groups()[0].lower().replace('_', '-')

            if source_name == 'pypi':
                # this is a special case
                source_name = PYPI_SOURCE

            source_urls[source_name] = val

    return source_urls


class DynamicOverrideSourcesPlugin(Plugin):
    """
    Allow dynamic overrides of repository URLs from environment variables.

    For mirror compatibility, LegacyRepository (PEP 503 API) is used instead of PyPiRepository.
    """
    def activate(self, poetry: Poetry, io: IO):

        pip_index_url = os.environ.get('PIP_INDEX_URL')

        source_urls = parse_environment_variables()

        for prioritized_repo in poetry.pool._sorted_repositories:
            repo = prioritized_repo.repository

            # if pip_index_url is set, override all repository urls.
            # otherwise, only override repository urls for those with an env var set.
            replace_with_url = pip_index_url if pip_index_url else source_urls.get(repo.name)

            if replace_with_url:
                # remove the existing repo and then add a new one to replace it
                poetry.pool.remove_repository(repo.name)
                poetry.pool.add_repository(
                    repository=SourceStrippedLegacyRepository(
                        repo.name,
                        replace_with_url,
                        config=poetry.config,
                        disable_cache=getattr(repo, '_disable_cache', None),
                    ),
                    default=(prioritized_repo.priority == Priority.DEFAULT),
                    secondary=(prioritized_repo.priority == Priority.SECONDARY),
                )


class SourceStrippedLegacyRepository(LegacyRepository):
    def __init__(
        self,
        name: str,
        url: str,
        config: Config | None = None,
        disable_cache: bool = False,
    ) -> None:
        super().__init__(name, url, config, disable_cache)
    # Packages sourced from PyPiRepository repositories *do not* include their
    # source data in poetry.lock. This is unique to PyPiRepository. Packages
    # sourced from LegacyRepository repositories *do* include their source data
    # (type, url, reference) in poetry.lock. This becomes undesirable when we
    # replace the PyPiRepository with a LegacyRepository PyPI mirror, as the
    # LegacyRepository begins to write source data into the project. We want to
    # support mirror use without referencing the mirror repository within the
    # project, so this behavior is undesired.
    #
    # To work around this, we extend LegacyRepository. The extended version
    # drops source URL information from packages attributed to the repository,
    # preventing that source information from being included in the lockfile.
    def package(
        self, name: str, version: Version, extras: list[str] | None = None
    ) -> Package:
        try:
            index = self._packages.index(Package(name, version))
            package = self._packages[index]
        except ValueError:
            package = super().package(name, version, extras)
        # It is a bit uncomfortable for this plugin to be modifying an internal
        # attribute of the package object. That said, the parent class does the
        # same thing (although it's not released independently like this plugin
        # is). It'd be preferable if there was a way to convey our goal
        # explicitly to poetry so we could avoid unintentional breaking changes.
        #
        # As one example of the potential danger, the existence of a non-None
        # package._source_url value currently determines if source data will be
        # written to poetry.lock. If this conditional changes, users of the
        # plugin may suddenly see unexpected source entries in their lockfiles.
        package._source_url = None
        return package
