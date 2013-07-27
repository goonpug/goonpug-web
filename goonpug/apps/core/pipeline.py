# -*- coding: utf-8 -*-
# Copyright (c) 2013 Peter Rowlands
# All rights reserved.
"""Overrides for the django social auth pipeline"""

from social_auth.models import UserSocialAuth
from social_auth.utils import setting


def _ignore_field(name, is_new=False):
    return name in ('id', 'pk') or \
        (not is_new and
         name in setting('SOCIAL_AUTH_PROTECTED_USER_FIELDS', []))


def create_user(backend, details, response, uid, username, user=None, *args,
                **kwargs):
    """Create user. Depends on get_username pipeline."""
    if user:
        return {'user': user}
    if not username:
        return None

    return {
        'user': UserSocialAuth.create_user(
            username=username, steamid=int(uid)),
        'original_email': '',
        'is_new': True
    }


def update_user_details(backend, details, response, user=None, is_new=False,
                        *args, **kwargs):
    """Update user details using data from provider."""
    if user is None:
        return

    changed = False  # flag to track changes

    for name, value in details.iteritems():
        # configured fields if user already existed
        if not _ignore_field(name, is_new):
            if value and value != getattr(user, name, None):
                setattr(user, name, value)
                changed = True

    # special case for steam backend
    if 'player' in details:
        for name, value in details['player'].iteritems():
            if not _ignore_field(name, is_new):
                if value and value != getattr(user, name, None):
                    setattr(user, name, value)
                    changed = True

    if changed:
        user.save()
