from http import HTTPStatus
from typing import TYPE_CHECKING, Dict

import pytest
from django.test import Client
from django.urls import reverse


if TYPE_CHECKING:
    from tests.plugins.identity.user import (
        RegistrationDataFactory,
        UserAssertion,
        UserData,
    )


@pytest.mark.django_db()
def test_update_succesful(  # noqa: WPS211
    signup_user: Dict[str, str],
    client: Client,
    registration_data_factory: "RegistrationDataFactory",
    assert_correct_user: "UserAssertion",
    expected_user_data: "UserData",
) -> None:
    """Update works with correct user data."""
    post_data = registration_data_factory(
        # Everything new, except email
        email=signup_user["username"],
    )

    response = client.post(
        reverse("identity:user_update"),
        data=post_data,
    )

    assert response.status_code == HTTPStatus.FOUND
    url = f"{reverse('identity:login')}?next={reverse('identity:user_update')}"
    assert response.get("Location") == url
    
    assert_correct_user(
        signup_user["username"],
        expected_user_data,
    )
