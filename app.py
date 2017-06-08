from bokeh.io import curdoc
from bokeh.layouts import row
from bokeh.plotting import figure
from bokeh.palettes import inferno
from bokeh.models import ColumnDataSource
from bokeh.embed import components
from bokeh.resources import INLINE
from utils.data import load_sequence_and_metadata

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
        .apply(lambda x: str(x))

    p = figure(plot_width=350, plot_height=200, tools='pan,reset')
    p.xaxis.axis_label = 'Year'
    p.yaxis.axis_label = 'Vaccine Effectiveness (%)'
    p.line(x=df['Season Start'], y=df['Overall VE'])
    p.circle(x=df['Season Start'], y=df['Overall VE'])
    return components(p)


def make_coordinate_scatterplot(coords, src):

    cx, cy = coords
    p = figure(webgl=True, plot_height=300, plot_width=300,
               tools='pan,box_select,reset')
    p.scatter(x='coords{0}'.format(cx),
              y='coords{0}'.format(cy),
              color='palette', source=src)

    p.xaxis.axis_label = 'Dimension {0}'.format(cx)
    p.yaxis.axis_label = 'Dimension {0}'.format(cy)

    return p


def make_coord_plots():
    p1 = make_coordinate_scatterplot([0, 1], src)
    p2 = make_coordinate_scatterplot([1, 2], src)
    p2.x_range = p1.y_range
    p3 = make_coordinate_scatterplot([0, 2], src)
    p3.x_range = p1.x_range
    p3.y_range = p2.y_range

    r1 = row(p1, p2, p3)

    evo_script, evo_div = components(r1)

    return evo_script, evo_div


def make_num_sequences_per_year_plot():
    sequences, metadata = load_sequence_and_metadata()
    metadata['Year'] = metadata['Collection Date'].apply(lambda x: x.year)
    metadata = metadata[metadata['Host Species'] == 'IRD:Human']
    gb = metadata.groupby('Year').count()

    p = figure(plot_width=350, plot_height=200, tools='pan,reset')
    p.line(gb['Name'].index, gb['Name'])
    p.xaxis.axis_label = 'Year'
    p.yaxis.axis_label = 'Number of Sequences'

    meta = dict()
    meta['n_seqs'] = len(metadata)
    meta['min_year'] = min(metadata['Year'])
    meta['max_year'] = max(metadata['Year'])
    return components(p), meta


@app.route('/')
def home():

    ve_script, ve_div = make_vaccine_effectiveness_plot()
    (nseq_script, nseq_div), (nseq_metadata) = make_num_sequences_per_year_plot()
    evo_script, evo_div = make_coord_plots()
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    seqs = [s for s in SeqIO.parse('data/oneQ_predictions.fasta', 'fasta')]
    n_seqs = len(seqs)

    return render_template('index.html', js_resources=js_resources,
                           css_resources=css_resources,
                           evo_script=evo_script, evo_div=evo_div,
                           nseq_script=nseq_script, nseq_div=nseq_div,
                           nseq_metadata=nseq_metadata,
                           n_seqs=n_seqs, ve_script=ve_script, ve_div=ve_div)


if __name__ == '__main__':
    app.run(debug=True)
