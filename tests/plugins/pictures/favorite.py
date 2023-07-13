from typing import Protocol, TypedDict, final

import pytest
from django_fakery.faker_factory import Factory
from mimesis.schema import Field, Schema
from typing_extensions import Unpack

from server.apps.pictures.models import FavouritePicture


class FavouritePictureData(TypedDict, total=False):
    """Data to create a `FavouritePicture`."""

    foreign_id: int
    url: str


@final
class FavouritePictureDataFactory(Protocol):  # type: ignore[misc]
    """A factory to generate `FavouritePictureData`."""

    def __call__(
        self,
        **fields: Unpack[FavouritePictureData],
    ) -> FavouritePictureData:
        """`FavouritePictureData` factory protocol."""


@pytest.fixture()
def mf(faker_seed: int) -> Field:
    """Returns the current mimesis `Field`."""
    return Field(seed=faker_seed)


@pytest.fixture()
def favourite_picture_data_factory(mf: Field):
    """Returns a factory to generate a `FavouritePictureData` dictionary."""
    schema = Schema(
        schema=lambda: {
            'foreign_id': mf('numeric.increment'),
            'url': mf('internet.url'),
        },
    )
    return lambda **fields: next(schema.iterator(1)) | fields


@pytest.fixture()
def favourite_picture_data(
    favourite_picture_data_factory: FavouritePictureDataFactory,
) -> FavouritePictureData:
    """Generates a `FavouritePictureData`."""
    return favourite_picture_data_factory()


@final
class FavouritePictureFactory(Protocol):  # type: ignore[misc]
    """A factory to generate a `FavouritePicture` instance."""

    def __call__(self, **fields) -> FavouritePicture:
        """`FavouritePicture` factory protocol."""


@pytest.fixture()
def favourite_picture_factory(
    fakery: Factory[FavouritePicture],
    faker_seed: int,
    default_password: str,
) -> FavouritePictureFactory:
    """Creates a factory to generate a `FavouritePicture` instance."""
    def factory(**fields):
        return fakery.make(  # type: ignore[call-overload]
            model=FavouritePicture,
            fields=fields,
            seed=faker_seed,
        )
    return factory
