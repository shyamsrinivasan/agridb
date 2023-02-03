from agriapp.data.models import Yields
from agriapp import db
from datetime import datetime as dt
from datetime import date


def get_yield(yield_obj=None, by_season=False, by_year=False, by_location=False, **kwargs):
    """function factory for querying yields"""
    if by_season:
        return yield_by_season(season=kwargs['season'], yield_obj=yield_obj)

    if by_year:
        return yield_by_year(year=kwargs['year'], yield_obj=yield_obj)

    if by_location:
        return yield_by_location(location=kwargs['location'], yield_obj=yield_obj)

    return None


def yield_by_season(season, yield_obj=None):
    """return all yields for given season (for all years)"""

    if yield_obj is not None:
        yield_obj = yield_obj.session.query(Yields).filter(Yields.season == season)
        return yield_obj

    yield_obj = db.session.query(Yields).filter(Yields.season == season)
    return yield_obj


def yield_by_year(year, yield_obj=None):
    """return all yields for given year (for all seasons)"""

    if yield_obj is not None:
        yield_obj = yield_obj.session.query(Yields).filter(Yields.year == year)
        return yield_obj

    yield_obj = db.session.query(Yields).filter(Yields.year == year)
    return yield_obj


def yield_by_location(location, yield_obj=None):
    """return all yields for given location (for all seasons and years)"""

    if yield_obj is not None:
        yield_obj = yield_obj.session.query(Yields).filter(Yields.location == location)
        return yield_obj

    yield_obj = db.session.query(Yields).filter(Yields.location == location)
    return yield_obj


def get_seasons(given_date=None):
    """get season name based on given date/month"""

    if given_date is None:
        given_date = dt.now()

    month = given_date.month
    if 4 <= month <= 8:
        return 'summer'

    if 1 <= month <= 2 or 9 <= month <= 12:
        return 'monsoon'

    if 3 <= month <= 4:
        return 'other'
