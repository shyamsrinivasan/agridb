from agriapp.data.models import Yields, Fields
from agriapp import db
from datetime import datetime as dt


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


def get_grouped_yields(by_season=False, by_buyer=False, yield_obj=None):
    """get location based yields grouped by different criteria"""
    if by_season:
        return get_total_yields_by_season(yield_obj)
    elif by_buyer:
        return get_total_yields_by_buyer(yield_obj)
    else:
        return None


def get_total_yields_by_season(yield_obj=None):
    """get total yields grouped by location and season"""
    if yield_obj is None:
        yield_obj = db.session.query(Yields).group_by(Yields.location, Yields.season)

    yield_obj = yield_obj.session.query(Yields.location,
                                        Yields.season,
                                        db.func.sum(Yields.weight)).group_by(Yields.location)
    return yield_obj


def get_total_yields_by_buyer(yield_obj=None):
    """get total yields grouped by season and buyer"""
    if yield_obj is None:
        yield_obj = db.session.query(Yields).group_by(Yields.season,
                                                      Yields.buyer)

    yield_obj = yield_obj.session.query(db.func.sum(Yields.weight),
                                        Yields.season, Yields.buyer).group_by(Yields.season,
                                                                              Yields.buyer)
    return yield_obj


def yield_per_acre_by_location(yield_obj=None):
    """get average yield per location"""

    if yield_obj is None:
        yield_obj = get_grouped_yields(by_season=True)

    # field_names = yield_obj.session.query(Yields.location).distinct().all()
    # location_names = [i_val[0] for i_val in field_names]
    values = yield_obj.all()
    field_extent = [(i_value[0], i_value[1], i_value[2],
                     db.session.query(Fields.field_extent).
                     filter(Fields.location == i_value[0]).first()) for i_value in values]
    yield_per_acre = [(i_value[0], i_value[1], i_value[2],
                       i_value[3][0], i_value[2]/i_value[3][0]) for i_value in field_extent]

    return yield_per_acre


# yield_obj = db.session.query(Yields).group_by(Yields.location, Yields.season)
    # yield_obj = yield_obj.session.query(Yields.location,
    #                                     Yields.season,
    #                                     db.func.sum(Yields.weight)).group_by(Yields.location)

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
