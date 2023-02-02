from flask import render_template, redirect, url_for
from bokeh.embed import components
from bokeh.plotting import figure
from . import visual_bp
from agriapp.data import models
from agriapp import db


@visual_bp.route('/yield', methods=['GET'])
def visualize_yield():
    # get all yield data
    yield_obj = db.session.query()
    yield_obj = db.session.query(models.Yields).filter(models.Yields.year == '2022',
                                                       models.Yields.season == 'summer').all()
    locations = [i_yield.location for i_yield in yield_obj]


    # p = figure(x_range=locations, height=350, title="Yields",
    #            sizing_mode='stretch_width', toolbar_location=None, tools="")
    #
    # p.vbar(x=locations, )
    return redirect(url_for('admin.homepage'))
