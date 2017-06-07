from bokeh.io import curdoc
from bokeh.layouts import row
from bokeh.plotting import figure
from bokeh.palettes import inferno
from bokeh.models import ColumnDataSource
from bokeh.embed import components
from bokeh.resources import INLINE

import pandas as pd
import os
from Bio import SeqIO

from flask import Flask, render_template

app = Flask(__name__)

data = pd.read_csv('https://raw.githubusercontent.com/ericmjl/flu-sequence-predictor/master/data/metadata_with_embeddings.csv',
                   index_col=0, parse_dates=['Collection Date'])
data = data.set_index('Collection Date').resample('Q').mean()
palette = inferno(len(data))
data['palette'] = palette

src = ColumnDataSource(data)


def make_vaccine_effectiveness_plot():
    tables = pd.read_html('https://www.cdc.gov/flu/professionals/vaccination/effectiveness-studies.htm')
    df = tables[0]
    df.columns = df.loc[0, :]
    df = df.drop(0).reset_index(drop=True)
    df.columns = ['Season', 'Reference', 'Study Sites', 'Number of Patients',
                  'Overall VE', 'CI']
    df['Season Start'] = df['Season'].str.split('-').str[0]\
        .apply(lambda x: int(x))

    p = figure(plot_width=300, plot_height=250)
    p.xaxis.axis_label = 'Year'
    p.yaxis.axis_label = 'Vaccine Effectiveness (%)'
    p.line(x=df['Season Start'], y=df['Overall VE'])
    p.circle(x=df['Season Start'], y=df['Overall VE'])
    return components(p)


def make_coordinate_scatterplot(coords):
    cx, cy = coords
    p = figure(webgl=True, plot_height=300, plot_width=300,
               tools='reset,box_select,pan')
    p.scatter(x='coords{0}'.format(cx),
              y='coords{0}'.format(cy),
              color='palette', source=src)

    p.xaxis.axis_label = 'Dimension {0}'.format(cx)
    p.yaxis.axis_label = 'Dimension {0}'.format(cy)

    return p


def make_coord_plots():
    p1 = make_coordinate_scatterplot([0, 1])
    p2 = make_coordinate_scatterplot([1, 2])
    p2.x_range = p1.y_range
    p3 = make_coordinate_scatterplot([0, 2])
    p3.x_range = p1.x_range
    p3.y_range = p2.y_range

    r1 = row(p1, p3)
    r2 = row(p2)

    curdoc().add_root(r1)
    curdoc().add_root(r2)
    curdoc().title = 'Viral evolution coordinates'

    script1, div1 = components(p1)
    script2, div2 = components(p2)
    script3, div3 = components(p3)

    return script1, div1, script2, div2, script3, div3


@app.route('/')
def home():

    ve_script, ve_div = make_vaccine_effectiveness_plot()
    script1, div1, script2, div2, script3, div3 = make_coord_plots()
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    seqs = [s for s in SeqIO.parse('data/oneQ_predictions.fasta', 'fasta')]
    n_seqs = len(seqs)

    return render_template('index.html', js_resources=js_resources,
                           css_resources=css_resources,
                           script1=script1, div1=div1,
                           script2=script2, div2=div2,
                           script3=script3, div3=div3, cwd=os.getcwd(),
                           n_seqs=n_seqs, ve_script=ve_script, ve_div=ve_div)


if __name__ == '__main__':
    app.run(debug=True)
