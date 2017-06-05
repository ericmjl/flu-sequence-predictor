from bokeh.io import curdoc
from bokeh.layouts import row
from bokeh.plotting import figure
from bokeh.palettes import inferno
from bokeh.models import ColumnDataSource

import pandas as pd

data = pd.read_csv('data/metadata_with_embeddings.csv', index_col=0,
                   parse_dates=['Collection Date'])
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
