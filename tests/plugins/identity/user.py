import datetime
from typing import Callable, Dict, Protocol, TypedDict, final

import pytest
from django_fakery.faker_factory import Factory
from mimesis.schema import Field, Schema
from typing_extensions import TypeAlias, Unpack

from server.apps.identity.models import User

USER_BIRTHDAY_FORMAT = "%Y-%m-%d"


class UserData(TypedDict, total=False):
    """
    Represent the simplified user data that is required to create a new user.
    It does not include ``password``, because it is very special in django.
    Importing this type is only allowed under ``if TYPE_CHECKING`` in tests.
    """

    email: str
    first_name: str
    last_name: str
    date_of_birth: datetime.datetime
    address: str
    job_title: str
    phone: str


@final
class SignedUpData(UserData, total=False):
    # special
    password: str


@final
class RegistrationData(UserData, total=False):
    """
    Represent the registration data that is required to create a new user.
    Importing this type is only allowed under ``if TYPE_CHECKING`` in tests.
    """

    password1: str
    password2: str


@final
class RegistrationDataFactory(Protocol):  # type: ignore[misc]
    def __call__(
        self,
        **fields: Unpack[RegistrationData],
    ) -> RegistrationData:
        """User data factory protocol."""


@pytest.fixture(scope="function")
def registration_data_factory(
    mf: Field,
) -> RegistrationDataFactory:
    """Returns factory for fake random data for regitration."""

    def factory(**fields: Unpack[RegistrationData]) -> RegistrationData:
        password = mf("password")  # by default passwords are equal
        schema = Schema(
            schema=lambda: {
                "email": mf("person.email"),
                "first_name": mf("person.first_name"),
                "last_name": mf("person.last_name"),
                "date_of_birth": mf("datetime.date"),
                "address": mf("address.city"),
                "job_title": mf("person.occupation"),
                "phone": mf("person.telephone"),
            }
        )
        return {
            **schema.create(iterations=1)[0],  # type: ignore[misc]
            **{"password1": password, "password2": password},
            **fields,
        }

    return factory


@pytest.fixture(scope="function")
def registration_data(
    registration_data_factory: RegistrationDataFactory,
) -> RegistrationData:
    """Default success registration data."""
    return registration_data_factory()


UserAssertion: TypeAlias = Callable[[str, UserData], None]


@pytest.fixture(scope="session")
def assert_correct_user() -> UserAssertion:
    def factory(email: str, expected: UserData) -> None:
        user = User.objects.get(email=email)
        # Special fields:
        assert user.id
        assert user.is_active
        assert not user.is_superuser
        assert not user.is_staff
        # All other fields:
        for field_name, data_value in expected.items():
            assert getattr(user, field_name) == data_value

    return factory


@pytest.fixture(scope="function")
def user_data(registration_data: "RegistrationData") -> "UserData":
    """
    We need to simplify registration data to drop passwords.
    Basically, it is the same as ``registration_data``, but without passwords.
    """

    return {  # type: ignore[return-value]
        key_name: value_part
        for key_name, value_part in registration_data.items()
        if not key_name.startswith("password")
    }


@pytest.fixture(scope="function")
def expected_user_data(
    registration_data: "RegistrationData",
) -> "UserData":
    """Expectd data for a Registrered user."""
    return {  # type: ignore[return-value]
        key_name: value_part
        for key_name, value_part in registration_data.items()
        if not key_name.startswith("password")
    }


@pytest.fixture(scope="function")
def signedup_data(registration_data: "RegistrationData") -> "SignedUpData":
    return {  # type: ignore [return-value]
        ("password" if key_name.startswith("password") else key_name): value_part
        for key_name, value_part in registration_data.items()
    }


@pytest.fixture(scope="function")
def created_user(signedup_data: "SignedUpData") -> User:
    return User.objects.create_user(**signedup_data)


@pytest.fixture(scope="function")
def signup_user(signedup_data: "SignedUpData", created_user: "User") -> Dict[str, str]:
    # User.objects.create_user(**signedup_data)
    return {
        "username": signedup_data["email"],
        "password": signedup_data["password"],
    }


@pytest.fixture(scope="function")
def user_email(mf) -> str:
    """Email of the current user."""
    return mf("person.email")


@pytest.fixture(scope="function")
def default_password(mf) -> str:
    """Default password for user factory."""
    return mf("person.password")


@pytest.fixture(scope="function")
def user_password(default_password) -> str:
    """Password of the current user."""
    return default_password


@final
class UserFactory(Protocol):  # type: ignore[misc]
    """A factory to generate a `User` instance."""

    def __call__(self, **fields) -> User:
        """Profile data factory protocol."""


@pytest.fixture(scope="function")
def user_factory(
    fakery: Factory[User],
    faker_seed: int,
    default_password: str,
) -> UserFactory:
    """Creates a factory to generate a user instance."""
    def factory(**fields):
        password = fields.pop('password', default_password)
        return fakery.make(  # type: ignore[call-overload]
            model=User,
            fields=fields,
            seed=faker_seed,
            pre_save=[lambda _user: _user.set_password(password)],
        )
    return factory


@pytest.fixture(scope="function")
def user(
    user_factory: UserFactory,
    user_email: str,
    user_password: str,
) -> User:
    """The current user.
    The fixtures `user_email` and `user_password` are used
    as email and password of the user correspondingly.
    """
    return user_factory(
        email=user_email,
        password=user_password,
        is_active=True,
    )
