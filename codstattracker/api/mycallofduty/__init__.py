from requests import Session

from codstattracker.api.interfaces import PlayerAPI
from codstattracker.api.mycallofduty.mw import PlayerAPI as _PlayerAPI


def api_factory(act_sso_cookie: str) -> PlayerAPI:
    session = Session()
    session.cookies.set('ACT_SSO_COOKIE', act_sso_cookie)
    return _PlayerAPI(session)
