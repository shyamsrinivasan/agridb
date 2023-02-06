from flask import render_template, redirect, url_for, flash
from bokeh.embed import components
from bokeh.plotting import figure
from . import visual_bp
from agriapp.data.models import Yields
from agriapp.analytics import methods

from agriapp import db


@visual_bp.route('/yield', methods=['GET'])
def visualize_yield():
    # get all yield data
    # yield_obj = db.session.query(Yields).group_by(Yields.location, Yields.season)
    # yield_obj = yield_obj.session.query(Yields.location,
    #                                     Yields.season,
    #                                     db.func.sum(Yields.weight)).group_by(Yields.location)
    yield_obj = methods.get_grouped_yields(by_season=True)
    values = methods.yield_per_acre_by_location(yield_obj)
    # values = yield_obj.all()

    if values and values is not None:
        # yield_obj = db.session.query(models.Yields).filter(models.Yields.year == '2022',
        #                                                    models.Yields.season == 'summer').all()
        locations = [i_value[0] for i_value in values]
        total_yield = [i_value[2] for i_value in values]
        per_acre_yield = [i_value[4] for i_value in values]

        # figure 1
        p1 = figure(title="Recent Yields", height=380,
                    toolbar_location=None, tools="")
        # sizing_mode = "stretch_width"
        y = [val for val in range(1, len(locations) + 1)]
        ticker_label = {val: locations[val-1].capitalize() for val in range(1, len(locations) + 1)}

        p1.hbar(y=y, right=total_yield, height=0.5)
        # plot propreties
        p1.ygrid.grid_line_color = None
        p1.x_range.start = 0
        # xaxis
        p1.xaxis.axis_label = 'Grain Yield (Metric Tons)'
        p1.xaxis.axis_label_text_font_size = '12pt'
        p1.xaxis.major_label_text_font_size = '12pt'
        # yaxis
        p1.yaxis.major_label_overrides = ticker_label
        p1.yaxis.minor_tick_line_color = None
        p1.yaxis.major_label_text_font_size = '12pt'

        # figure 2
        p2 = figure(title="Recent Yield/Acre", height=380,
                    toolbar_location=None, tools="")
        p2.hbar(y=y, right=per_acre_yield, height=0.5)
        # plot propreties
        p2.ygrid.grid_line_color = None
        p2.x_range.start = 0
        # xaxis
        p2.xaxis.axis_label = 'Grain Yield (Metric Tons/Acre)'
        p2.xaxis.axis_label_text_font_size = '12pt'
        p2.xaxis.major_label_text_font_size = '12pt'
        # yaxis
        p2.yaxis.major_label_overrides = ticker_label
        p2.yaxis.minor_tick_line_color = None
        p2.yaxis.major_label_text_font_size = '12pt'

        # vbar
        # p2 = figure(x_range=locations, height=350, width=300,
        #             title="Recent Yield/Acre",
        #             toolbar_location=None, tools="")
        # p2.vbar(x=locations, top=per_acre_yield, width=0.9)
        # p2.xaxis.axis_line_width
        # p2.xaxis.axis_line_color
        # p2.xaxis.axis_label_text_font_style
        # p2.xaxis.axis_label_text_font

        # graph components for jinja template use
        script, div = components(p1)
        script2, div2 = components(p2)

        return render_template('plot_yields.html',
                               script=[script, script2],
                               div=[div, div2])

    flash(message='No yield data available to visualize', category='primary')
    return redirect(url_for('admin.homepage'))
