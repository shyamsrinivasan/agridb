from agriapp.data.models import Yields, Fields
from agriapp import db
from datetime import datetime as dt
from datetime import timedelta
import pandas as pd


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


def get_grouped_yields(by_season=False, by_buyer=False,
                       yield_obj=None, year=None):
    """get location based yields grouped by different criteria"""
    if by_season:
        if year is not None:
            return total_yields_by_season(year, yield_obj)
        else:
            return total_yearly_yields_by_season(yield_obj)
    elif by_buyer:
        return total_yields_by_buyer(yield_obj)
    else:
        return None


def total_yields_by_season(year, yield_obj=None):
    """get total yields grouped by location and season"""
    if yield_obj is None:
        yield_obj = db.session.query(Yields).group_by(Yields.location, Yields.season)

    yield_obj = yield_obj.session.query(Yields.location,
                                        Yields.season,
                                        db.func.sum(Yields.weight)).filter(Yields.year == year).\
        group_by(Yields.location, Yields.season)
    # add data from all years (cumulative for all years)
    # yield_obj = yield_obj.session.query(Yields.location,
    #                                     Yields.season,
    #                                     db.func.sum(Yields.weight)). \
    #     group_by(Yields.location, Yields.season)

    return yield_obj


def total_yearly_yields_by_season(yield_obj=None):
    """get total yields for every year (separately)
    grouped by location and season"""
    if yield_obj is None:
        yield_obj = db.session.query(Yields).group_by(Yields.location, Yields.season, Yields.year)

    yield_obj = yield_obj.session.query(Yields.location,
                                        Yields.season,
                                        Yields.year,
                                        db.func.sum(Yields.weight)).group_by(Yields.location,
                                                                             Yields.season,
                                                                             Yields.year)
    return yield_obj


def total_yields_by_buyer(yield_obj=None):
    """get total yields grouped by season and buyer"""
    if yield_obj is None:
        yield_obj = db.session.query(Yields).group_by(Yields.season,
                                                      Yields.buyer)

    yield_obj = yield_obj.session.query(db.func.sum(Yields.weight),
                                        Yields.season, Yields.buyer).group_by(Yields.season,
                                                                              Yields.buyer)
    return yield_obj


def yield_per_acre_by_location(by_year=False, by_season=False, yield_obj=None):
    """get yield per acre based on location (factory)"""
    if by_year:
        return seasonal_yield_per_acre(yield_obj)
    elif by_season:
        return yearly_yield_per_acre(yield_obj)
    else:
        return None


def seasonal_yield_per_acre(yield_obj=None):
    """get yield per acre by location for a single year data
    segregated by seasons"""

    if yield_obj is None:
        yield_obj = get_grouped_yields(by_season=True, year='2021')

    # field_names = yield_obj.session.query(Yields.location).distinct().all()
    # location_names = [i_val[0] for i_val in field_names]
    values = yield_obj.all()
    field_extent = [(i_value[0], i_value[1], i_value[2],
                     db.session.query(Fields.field_extent).
                     filter(Fields.location == i_value[0]).first()) for i_value in values]
    yield_per_acre = [(i_value[0], i_value[1], i_value[2],
                       i_value[3][0], i_value[2]/i_value[3][0]) for i_value in field_extent]

    return yield_per_acre


def yearly_yield_per_acre(yield_obj=None):
    """get yield per acre by location across multiple years
    and seasons"""

    if yield_obj is None:
        yield_obj = get_grouped_yields(by_season=True)

    # field_names = yield_obj.session.query(Yields.location).distinct().all()
    # location_names = [i_val[0] for i_val in field_names]
    values = yield_obj.all()
    field_extent = [(i_value[0], i_value[1], i_value[2], i_value[3],
                     db.session.query(Fields.field_extent).
                     filter(Fields.location == i_value[0]).first()) for i_value in values]
    yield_per_acre = [(i_value[0], i_value[1], i_value[2], i_value[3],
                       i_value[4][0], i_value[3]/i_value[4][0]) for i_value in field_extent]

    return yield_per_acre


def get_current_past_year():
    """get current year and previous year using datetime"""
    current_year = dt.now().year
    past_year = dt.now() - timedelta(days=365)
    past_year = past_year.year

    return current_year, past_year


def quantile_calculation(data_df, classification="season"):
    """calculate 25%, 50% and 75% quantiles on grouped data"""

    if classification == "season":
        return seasonal_quantile_calculation(data_df)
    elif classification == "annual":
        return yearly_quantile_calculation(data_df)
    else:
        return None


def seasonal_quantile_calculation(data_df):
    """calculate quantile for each location for each season for multiple years"""
    df = data_df.groupby(["location", "season"])
    try:
        qs = df.production.quantile([.25, .5, .75])
    except AttributeError:
        qs = df.production_per_acre.quantile([.25, .5, .75])

    qs = qs.unstack().reset_index()
    qs.columns = ["location", "season", "q1", "q2", "q3"]
    # merged data with 1st, 2nd and 3rd quartiles
    full_df_with_qs = pd.merge(data_df, qs, on=["location", "season"], how="left")
    # IQR
    iqr = full_df_with_qs.q3 - full_df_with_qs.q1
    # IQR outlier bounds 1.5xIQR
    full_df_with_qs["upper"] = full_df_with_qs.q3 + 1.5 * iqr
    full_df_with_qs["lower"] = full_df_with_qs.q1 - 1.5 * iqr
    return full_df_with_qs


def yearly_quantile_calculation(data_df):
    """calculate quantile for each location for each year for multiple seasons"""
    df = data_df.groupby(["location", "year"])
    try:
        qs = df.production.quantile([.25, .5, .75])
    except AttributeError:
        qs = df.production_per_acre.quantile([.25, .5, .75])

    qs = qs.unstack().reset_index()
    qs.columns = ["location", "year", "q1", "q2", "q3"]
    # merged data with 1st, 2nd and 3rd quartiles
    full_df_with_qs = pd.merge(data_df, qs, on=["location", "year"], how="left")
    # IQR
    iqr = full_df_with_qs.q3 - full_df_with_qs.q1
    # IQR outlier bounds 1.5xIQR
    full_df_with_qs["upper"] = full_df_with_qs.q3 + 1.5 * iqr
    full_df_with_qs["lower"] = full_df_with_qs.q1 - 1.5 * iqr
    return full_df_with_qs


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



