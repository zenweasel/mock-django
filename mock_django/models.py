"""
mock_django.models
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

import mock
from datetime import datetime
from django.contrib.auth.models import User, AnonymousUser

__all__ = ('ModelMock', 'UserMock', )


# TODO: make foreignkey_id == foreignkey.id
class _ModelMock(mock.MagicMock):
    def _get_child_mock(self, **kwargs):
        name = kwargs.get('name', '')
        if name == 'pk':
            return self.id
        return super(_ModelMock, self)._get_child_mock(**kwargs)


def ModelMock(model):
    """
    >>> Post = ModelMock(Post)
    >>> assert post.pk == post.id
    """
    return _ModelMock(spec=model())


class MockUserManager():

    model = None

    @classmethod
    def normalize_email(cls, email):
        """
        Normalize the address by lowercasing the domain part of the email
        address.
        """
        email = email or ''
        try:
            email_name, domain_part = email.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email = '@'.join([email_name, domain_part.lower()])
        return email

    def create_user(self, username, email=None, password=None):
        """
        Creates and 'saves' a User with the given username, email and password.
        """
        now = datetime.now()
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)

        user = self.model(username=username, email=email,
                          is_staff=False, is_active=True, is_superuser=False,
                          last_login=now, date_joined=now)

        user.set_password(password)
        return user


class UserProfile(object):
    pass


def UserMock(username=None, password=None, authenticated=True, is_anonymous=False, is_staff=False):

    if is_anonymous:
        _user_mock = _ModelMock(AnonymousUser)
    else:
        _user_mock = _ModelMock(User)
    _user_mock.get_profile = mock.MagicMock(return_value=UserProfile())
    _user_mock.authenticated = authenticated
    _user_mock.is_anonymous = mock.Mock(return_value=is_anonymous)
    _user_mock.is_staff = is_staff
    _user_mock.is_active = True
    _mock_user_manager = MockUserManager()
    _mock_user_manager.model = _user_mock
    _user_mock.objects = _mock_user_manager
    _user_mock.username = username
    _user_mock.get_password = mock.MagicMock(return_value=password)
    return _user_mock
