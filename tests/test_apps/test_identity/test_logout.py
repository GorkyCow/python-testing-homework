from http import HTTPStatus
from typing import Dict

import pytest
from django.contrib import auth
from django.test import Client
from django.urls import reverse
from django.utils.crypto import get_random_string

from server.apps.identity.models import User


@pytest.mark.django_db()
def test_logout(user: User, client: Client):
    """Test a registred user can login."""
    client.force_login(user)

    response = client.post(reverse("identity:logout"))
    logouted_user = auth.get_user(client)

    assert response.status_code == HTTPStatus.FOUND
    assert not logouted_user.is_authenticated
    assert response.get("location") == "/"
