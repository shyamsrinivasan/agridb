from flask import render_template, redirect, url_for, flash
from bokeh.embed import components
from bokeh.plotting import figure, show
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

        p = figure(x_range=locations, height=350,
                   title="Recent Yields by Location", sizing_mode='stretch_width', toolbar_location=None, tools="")
        p.vbar(x=locations, top=weights, width=0.9)

        p.xgrid.grid_line_color = None
        p.y_range.start = 0

        script, div = components(p)
        # show(p)
        return render_template('plot_yields.html', script=script, div=div)

    flash(message='No yield data available to visualize', category='primary')
    return redirect(url_for('admin.homepage'))
