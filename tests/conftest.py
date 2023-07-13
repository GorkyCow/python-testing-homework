"""
This module is used to provide configuration, fixtures, and plugins for pytest.

It may be also used for extending doctest's context:
1. https://docs.python.org/3/library/doctest.html
2. https://docs.pytest.org/en/latest/doctest.html
"""
import random

import pytest
from django.test.client import Client
from mimesis.schema import Field

from server.apps.identity.models import User


pytest_plugins = [
    # Should be the first custom one:
    "plugins.django_settings",
    # TODO: add your own plugins here!
    "plugins.djano_form_view",
    "plugins.identity.user",
    "plugins.pictures.favorite",
]


@pytest.fixture(scope="session")
def faker_seed() -> int:
    """Generates random seed for a fake data."""
    return random.Random().getrandbits(32)


@pytest.fixture(scope="function")
def user_client(user: User) -> Client:
    """A Django test client logged in as the current user."""
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture(scope="function")
def mf(faker_seed: int) -> Field:
    """Returns the current mimesis `Field`."""

    return Field(seed=faker_seed)
