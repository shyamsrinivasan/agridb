from flask import render_template, redirect, url_for, flash
from bokeh.embed import components
from bokeh.plotting import figure
from . import visual_bp
from agriapp.data.models import Yields
from agriapp import db


@visual_bp.route('/yield', methods=['GET'])
def visualize_yield():
    # get all yield data
    yield_obj = db.session.query(Yields).group_by(Yields.location, Yields.season)
    yield_obj = yield_obj.session.query(Yields.location,
                                        Yields.season,
                                        db.func.sum(Yields.weight)).group_by(Yields.location)
    values = yield_obj.all()

    if values and values is not None:
        # yield_obj = db.session.query(models.Yields).filter(models.Yields.year == '2022',
        #                                                    models.Yields.season == 'summer').all()
        locations = [i_value[0] for i_value in values]
        weights = [i_value[2] for i_value in values]

        # p = figure(x_range=locations, height=350,
        #            title="Recent Yields by Location", sizing_mode='stretch_width',
        #            toolbar_location=None, tools="")
        # p.vbar(x=locations, top=weights, width=0.9)
        #
        # p.xgrid.grid_line_color = None
        # p.y_range.start = 0
        # p.yaxis.axis_label = 'Grain Yield (Metric Tons)'
        # # graph components for jinja template use
        # script, div = components(p)
        #
        p2 = figure(title="Recent Yields", height=380, width=700,
                    toolbar_location=None, tools="")
        # sizing_mode = "stretch_width"
        y = [val for val in range(1, len(locations) + 1)]
        ticker_label = {val: locations[val-1].capitalize() for val in range(1, len(locations) + 1)}

        p2.hbar(y=y, right=weights, height=0.5)

        # plot propreties
        p2.ygrid.grid_line_color = None
        p2.x_range.start = 0
        p2.xaxis.axis_label = 'Grain Yield (Metric Tons)'
        p2.xaxis.axis_label_text_font_size = '14pt'
        p2.xaxis.major_label_text_font_size = '14pt'
        # p2.xaxis.axis_line_width
        # p2.xaxis.axis_line_color
        # p2.xaxis.axis_label_text_font_style
        # p2.xaxis.axis_label_text_font

        p2.yaxis.major_label_overrides = ticker_label
        p2.yaxis.minor_tick_line_color = None
        p2.yaxis.major_label_text_font_size = '16pt'

        script2, div2 = components((p2))

        return render_template('plot_yields.html',
                               script=[script2],
                               div=[div2])

    flash(message='No yield data available to visualize', category='primary')
    return redirect(url_for('admin.homepage'))
