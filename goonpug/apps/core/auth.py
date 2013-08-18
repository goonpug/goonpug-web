# -*- coding: utf-8 -*-
# Copyright (c) 2013 Astroman Technologies LLC
# All rights reserved.
#
import urllib
import urllib2

from django.utils import simplejson

from social_auth.utils import setting
from social_auth.backends.steam import SteamAuth, SteamBackend, USER_INFO


class GoonpugSteamBackend(SteamBackend):

    def get_user_details(self, response):
        user_id = self._user_id(response)
        url = USER_INFO + urllib.urlencode({'key': setting('STEAM_API_KEY'),
                                            'steamids': user_id})
        details = {}
        try:
            player = simplejson.load(urllib2.urlopen(url))
        except (ValueError, IOError):
            pass
        else:
            if len(player['response']['players']) > 0:
                player = player['response']['players'][0]
                details = {'username': player.get('steamid'),
                           'email': '',
                           'fullname': player.get('personaname'),
                           'first_name': '',
                           'last_name': '',
                           'player': player}
        return details


class GoonpugSteamAuth(SteamAuth):

    AUTH_BACKEND = GoonpugSteamBackend


BACKENDS = {
    'steam': GoonpugSteamAuth,
}
