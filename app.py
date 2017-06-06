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


def make_scatterplot(coords):
    cx, cy = coords
    p = figure(webgl=True, plot_height=300, plot_width=300,
               tools='reset,box_select,pan')
    p.scatter(x='coords{0}'.format(cx),
              y='coords{0}'.format(cy),
              color='palette', source=src)

    p.xaxis.axis_label = 'Dimension {0}'.format(cx)
    p.yaxis.axis_label = 'Dimension {0}'.format(cy)

    return p


@app.route('/')
def home():
    p1 = make_scatterplot([0, 1])
    p2 = make_scatterplot([1, 2])
    p2.x_range = p1.y_range
    p3 = make_scatterplot([0, 2])
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

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # print(script1, div1, script2, div2, script3, div3)

    seqs = [s for s in SeqIO.parse('data/oneQ_predictions.fasta', 'fasta')]
    n_seqs = len(seqs)

    return render_template('index.html', js_resources=js_resources,
                           css_resources=css_resources,
                           script1=script1, div1=div1,
                           script2=script2, div2=div2,
                           script3=script3, div3=div3, cwd=os.getcwd(),
                           n_seqs=n_seqs)


if __name__ == '__main__':
    app.run(debug=True)
