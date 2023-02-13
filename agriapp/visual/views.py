from flask import render_template, redirect, url_for, flash
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from bokeh.palettes import Colorblind
from collections import defaultdict
from . import visual_bp
from agriapp.data.models import Yields
from agriapp.analytics import methods

from agriapp import db


@visual_bp.route('/yield', methods=['GET'])
def visualize_yield():

    current_year, past_year = methods.get_current_past_year()
    # get current year yield
    yield_obj = db.session.query(Yields).filter(Yields.year == '2021')
    # get current year yield data grouped by seasons and location
    yield_obj = methods.get_grouped_yields(by_season=True, yield_obj=yield_obj)
    values = methods.yield_per_acre_by_location(yield_obj)

    # get past year yield

    if values and values is not None:
        # get unique seasons
        seasons = list(set([i_value[1] for i_value in values]))

        # final required data format
        # x = [(i_location, i_season) for i_location in yield_data['locations']
        #      for i_season in seasons]
        # counts = sum(zip(yield_data['monsoon'], yield_data['summer']), ())

        # group yield data by seasons and location for plot
        yield_data = defaultdict(list)
        yield_per_acre_data = defaultdict(list)
        for i_value in values:
            yield_data['x'].append((i_value[0], i_value[1]))
            yield_data['counts'].append(i_value[2])
            yield_per_acre_data['x'].append((i_value[0], i_value[1]))
            yield_per_acre_data['counts'].append(i_value[4])

        # figure 1 - yield
        script, div = make_grouped_vbar(data=yield_data, factors=seasons,
                                        y_axis_label='Grain Yield (Metric Tons)')

        # figure 2 - yield/acre
        script2, div2 = make_grouped_vbar(data=yield_per_acre_data, factors=seasons,
                                          y_axis_label='Grain Yield (Metric Tons/Acre)')

        return render_template('plot_yields.html',
                               script=[script, script2],
                               div=[div, div2])

    flash(message='No yield data available to visualize', category='primary')
    return redirect(url_for('admin.homepage'))


def make_grouped_vbar(data, factors=None, y_axis_label=None):
    """deliver jinja template script and div for a grouped vbar.
    E.g., For annual yield data Factors are location and season.
    Major axis label = season, Groups = location are provided as
    list of factors (location, season) in data['x'].
    Values are provided in data['counts'] for each factor in data['x'].
    Factors (Major axis labels) are provided in a separate list for use with
    color palettes"""

    source = ColumnDataSource(data=dict(x=data['x'],
                                        counts=tuple(data['counts'])))
    p1 = figure(x_range=FactorRange(*data['x']),
                title="Last Year ({}) Yields".format('2021'),
                height=600, width=900,
                toolbar_location=None, tools="")
    # sizing_mode = "stretch_width"
    # y = [val for val in range(1, len(locations) + 1)]
    # ticker_label = {val: locations[val-1].capitalize() for val in range(1, len(locations) + 1)}

    if factors is not None:
        # plot with color palette
        p1.vbar(x='x', top='counts', width=0.9, source=source, line_color="white",
                fill_color=factor_cmap('x', palette=Colorblind[3], factors=factors,
                                       start=1, end=2))
    else:
        # plot without color palette
        p1.vbar(x='x', top='counts', width=0.9, source=source)

    # plot propreties - xaxis
    p1.xgrid.grid_line_color = None
    p1.x_range.range_padding = 0.1
    p1.xaxis.major_label_orientation = 1
    # p1.yaxis.major_label_overrides = ticker_label
    # p1.yaxis.minor_tick_line_color = None
    p1.xaxis.major_label_text_font_size = '13pt'
    p1.xaxis.group_text_font_size = '13pt'
    p1.xaxis.group_text_color = 'black'
    # plot propreties - yaxis
    p1.y_range.start = 0
    if y_axis_label is not None:
        p1.yaxis.axis_label = y_axis_label
    p1.yaxis.axis_label_text_font_size = '13pt'
    p1.yaxis.major_label_text_font_size = '13pt'

    # graph components for jinja template use
    script, div = components(p1)

    # p2.hbar(y=y, right=per_acre_yield, height=0.5)
    # p2.xaxis.axis_line_width
    # p2.xaxis.axis_line_color
    # p2.xaxis.axis_label_text_font_style
    # p2.xaxis.axis_label_text_font
    # p2.yaxis.major_label_overrides = ticker_label
    # p2.yaxis.minor_tick_line_color = None

    return script, div
