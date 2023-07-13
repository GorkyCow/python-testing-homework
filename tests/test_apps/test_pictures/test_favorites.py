from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.test.client import Client

from server.apps.identity.models import User

if TYPE_CHECKING:
    from tests.plugins.pictures.favourite_picture import FavouritePictureFactory


pytestmark = pytest.mark.django_db


def test_favourite_picture_list(
    user: User,
    user_client: Client,
    favourite_picture_factory: 'FavouritePictureFactory',
):
    """Object list contains owned `FavouritePicture` only."""
    owned_favourite_picture = favourite_picture_factory(user=user)
    favourite_picture_factory()
    response = user_client.get('/pictures/favourites')
    assert response.status_code == HTTPStatus.OK
    object_list = list(
        response.context_data['object_list'],  # type: ignore[attr-defined]
    )
    assert object_list == [owned_favourite_picture]
