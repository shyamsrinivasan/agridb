import pandas as pd
from flask import render_template, redirect, url_for, flash
from bokeh.models import ColumnDataSource, FactorRange, Whisker
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from bokeh.palettes import Colorblind, Set2, TolRainbow5
from bokeh.sampledata.autompg2 import autompg2
from collections import defaultdict
from . import visual_bp
from agriapp.analytics import methods

from agriapp import db


@visual_bp.route('/yield', methods=['GET'])
def visualize_yield():
    """visualize yield data by querying data from db and
    display using bokeh plots. Plots shown
    1. Yield for previous and/or current year
    2. Yield/acre for previous and/or current year
    3. Yields for all years with available data"""

    current_year, past_year = methods.get_current_past_year()
    # get current/past year yield data grouped by seasons and location
    yield_obj = methods.get_grouped_yields(by_season=True, year='2021')
    values = methods.yield_per_acre_by_location(by_year=True, yield_obj=yield_obj)

    if values and values is not None:
        # get unique seasons
        seasons = list(set([i_value[1] for i_value in values]))

        # group yield data by seasons and location for plot
        yield_data = defaultdict(list)
        yield_per_acre_data = defaultdict(list)
        for i_value in values:
            yield_data['x'].append((i_value[0], i_value[1]))
            yield_data['counts'].append(i_value[2])
            yield_per_acre_data['x'].append((i_value[0], i_value[1]))
            yield_per_acre_data['counts'].append(i_value[4])

        # figure 1 - yield
        properties = {'title': "Last Year ({}) Yields".format('2021'),
                      'y_axis_label': 'Grain Yield (Metric Tons)'}
        script, div = make_grouped_vbar(data=yield_data, factors=seasons,
                                        properties=properties)

        # figure 2 - yield/acre
        properties = {'title': "Last Year ({}) Yields/Acre".format('2021'),
                      'y_axis_label': 'Grain Yield (Metric Tons/Acre)'}
        script2, div2 = make_grouped_vbar(data=yield_per_acre_data, factors=seasons,
                                          properties=properties)

        # get yield data grouped by year, season and location
        yearly_yield_obj = methods.get_grouped_yields(by_season=True)
        yearly_values = methods.yield_per_acre_by_location(by_season=True,
                                                           yield_obj=yearly_yield_obj)

        df = pd.DataFrame(yearly_values, columns=['location', 'season', 'year',
                                                  'yield', 'field_extent', 'yield/acre'])

        # unique factors
        locations = list(set([i_value[0] for i_value in yearly_values]))
        factors = list(set([(i_value[2], i_value[1]) for i_value in yearly_values]))
        # get data for each factor using pandas
        new_data = [return_yield_dict(df, i_factor) for i_factor in factors]
        max_total = max([i_value['total'] for i_value in new_data])

        # set missing data to 0
        for idata in new_data:
            for iloc in locations:
                if iloc not in idata['location']:
                    idata['location'].append(iloc)
                    idata['yield'].append(0)

        diff_data = defaultdict(list)
        for iloc in locations:
            diff_data[iloc] = [idata['yield'][indx] for idata in new_data
                               for indx, value in enumerate(idata['location']) if value == iloc]
        # add factors to data
        diff_data['x'] = factors
        cap_locations = [i_loc.capitalize() for i_loc in locations]
        # figure 3 - stacked yield plot (for multiple years)
        # showing total yield stacked by location
        script3, div3 = make_stacked_grouped_bar(diff_data, factors=factors,
                                                 stack=locations,
                                                 stack_legend=cap_locations,
                                                 y_axis_label='Total Grain Yield (Metric Tons)')

        # box plot of yields/acre at different locations for various years and seasons
        # (shows mean and median values)
        df1 = autompg2[["class", "hwy"]].rename(columns={"class": "kind"})
        # compute IQR
        qs = df1.groupby("kind").hwy.quantile([.25, .5, .75])
        qs = qs.unstack().reset_index()
        qs.columns = ["kind", "q1", "q2", "q3"]
        df1 = pd.merge(df1, qs, on="kind", how="left")

        yield_df = df[["location", "season", "year", "yield", "yield/acre"]].\
            rename(columns={"yield": "production", "yield/acre": "production_per_acre"})
        yield_qs = methods.quantile_calculation(yield_df[["location", "season", "year",
                                                          "production"]],
                                                classification="season")
        summer_yields = yield_qs[yield_qs["season"] == "summer"]
        source = ColumnDataSource(summer_yields)
        p = figure(x_range=summer_yields.location.unique())
        # outlier range
        whisker = Whisker(base="location", upper="upper", lower="lower", source=source)
        whisker.upper_head.size = whisker.lower_head.size = 20
        p.add_layout(whisker)
        # quantile boxes
        cmap = factor_cmap("location", "TolRainbow7", summer_yields.location.unique())
        p.vbar("location", 0.7, "q2", "q3", source=source, color=cmap, line_color="black")
        p.vbar("location", 0.7, "q1", "q2", source=source, color=cmap, line_color="black")
        # outliers
        outliers = summer_yields[~summer_yields.production.between(summer_yields.lower,
                                                                   summer_yields.upper)]
        p.scatter("location", "production", source=outliers, size=6, color="black", alpha=0.3)
        p.xgrid.grid_line_color = None
        p.axis.major_label_text_font_size = "14px"
        p.axis.axis_label_text_font_size = "12px"

        script4, div4 = components(p)

        yield_per_acre_qs = methods.quantile_calculation(yield_df[["location", "season",
                                                                   "year", "production_per_acre"]],
                                                         classification="season")

        return render_template('plot_yields.html',
                               script=[script, script2, script3, script4],
                               div=[div, div2, div3, div4])

    flash(message='No yield data available to visualize', category='primary')
    return redirect(url_for('admin.homepage'))


def return_yield_dict(df, factor):
    """return data for specific factor"""
    values = df[(df['season'] == factor[1]) & (df['year'] == factor[0])][['location', 'yield']].\
        to_dict(orient='list')
    values['total'] = sum(values['yield'])
    return values


def make_grouped_vbar(data, factors=None, properties=None):
    """deliver jinja template script and div for a grouped vbar.
    E.g., For annual yield data Factors are location and season.
    Major axis label = season, Groups = location are provided as
    list of factors (location, season) in data['x'].
    Values are provided in data['counts'] for each factor in data['x'].
    Factors (Major axis labels) are provided in a separate list for use with
    color palettes.

    Final required data format:
    x = [(i_location, i_season) for i_location in yield_data['locations']
        for i_season in seasons]
    counts = sum(zip(yield_data['monsoon'], yield_data['summer']), ())"""

    source = ColumnDataSource(data=dict(x=data['x'],
                                        counts=tuple(data['counts'])))
    if properties is not None and 'title' in properties.keys():
        p1 = figure(x_range=FactorRange(*data['x']),
                    title=properties['title'],
                    height=500, width=700,
                    toolbar_location=None, tools="")
    else:
        p1 = figure(x_range=FactorRange(*data['x']),
                    height=500, width=700,
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
    p1.y_range.end = max(data['counts'])
    p1.xaxis.major_label_orientation = 1
    # p1.yaxis.major_label_overrides = ticker_label
    # p1.yaxis.minor_tick_line_color = None
    p1.xaxis.major_label_text_font_size = '13pt'
    p1.xaxis.group_text_font_size = '13pt'
    p1.xaxis.group_text_color = 'black'
    # plot propreties - yaxis
    p1.y_range.start = 0
    if properties is not None and 'y_axis_label' in properties.keys():
        p1.yaxis.axis_label = properties['y_axis_label']
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


def make_stacked_grouped_bar(data, factors=None, stack=None, stack_legend=None,
                             y_axis_label=None):
    """delive jinja template dev and script for a grouped and stacked bar graph.
    data should be of the form
    data = {x = factors[(Y1, S1), (Y1, S2),...]
           l1 = []
           l2 = []}
    """

    # create source for bokeh plot
    source = ColumnDataSource(data=data)
    # figure 3 - stacked yields from mulitple years, seasons and locations
    p3 = figure(x_range=FactorRange(*factors), title='Annual yield comparison',
                height=500, width=700,
                toolbar_location=None, tools="")
    # stacked bar chart
    p3.vbar_stack(stack, x='x', width=0.3, color=Set2[5],
                  source=source, legend_label=stack_legend)
    # plot properties
    p3.x_range.range_padding = 0.1
    p3.xaxis.major_label_orientation = 1
    p3.xgrid.grid_line_color = None
    p3.xaxis.major_label_text_font_size = '14pt'
    p3.xaxis.group_text_font_size = '14pt'
    p3.xaxis.group_text_color = 'black'

    p3.y_range.start = 0
    if y_axis_label is not None:
        p3.yaxis.axis_label = y_axis_label
    # p3.y_range.end = 18
    p3.yaxis.axis_label_text_font_size = '14pt'
    p3.yaxis.major_label_text_font_size = '14pt'

    p3.legend.location = "top_left"
    p3.legend.orientation = "horizontal"

    script, div = components(p3)

    return script, div


def make_box_plot():
    """box plot to show yield spread between different seasons/years"""




