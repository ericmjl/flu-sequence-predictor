from bokeh.layouts import row
from bokeh.plotting import figure
from bokeh.palettes import inferno
from bokeh.models import (ColumnDataSource, Range1d, PanTool, HoverTool,
                          ResetTool, CrosshairTool)
from bokeh.embed import components
from utils.data import load_sequence_and_metadata, load_prediction_coordinates
from scipy.spatial import ConvexHull

import pandas as pd
import logging

logger = logging.getLogger('werkzeug')
logger.setLevel(logging.DEBUG)


def make_vaccine_effectiveness_plot():
    """
    This makes the plot that introduces vaccine effectiveness.
    """
    # Download and preprocess data.
    logger.debug('started making vaccine effectiveness plot.')
    cdc_tables = pd.read_html('https://www.cdc.gov/flu/professionals/vaccination/effectiveness-studies.htm')  # noqa
    cdc_ve = cdc_tables[0]
    cdc_ve.columns = cdc_ve.loc[0, :]
    cdc_ve = cdc_ve.drop(0).reset_index(drop=True)
    cdc_ve.columns = ['season', 'reference', 'study_sites', 'num_patients',
                  'overall_ve', 'CI']
    cdc_ve['season_start'] = cdc_ve['season'].str.split('-').str[0]\
        .apply(lambda x: str(x))
    logger.debug('downloaded and preprocessed vaccine effectiveness data.')

    # Configure Bokeh Plot
    cdc_src = ColumnDataSource(cdc_ve)
    hover_tool = HoverTool()
    hover_tool.tooltips = [
        ("Year", "@season_start"),
        ("Effectiveness", "@overall_ve")
    ]
    tools = [PanTool(), CrosshairTool(), hover_tool, ResetTool()]

    # Make Bokeh Plot
    p = figure(plot_width=350, plot_height=200,
               tools=tools)
    p.xaxis.axis_label = 'Year'
    p.yaxis.axis_label = 'Vaccine Effectiveness (%)'
    p.y_range = Range1d(0, 100)
    p.line(x='season_start', y='overall_ve', source=cdc_src)
    p.circle(x='season_start', y='overall_ve', source=cdc_src)
    logger.debug('made bokeh plot')
    return components(p)


def make_num_sequences_per_year_plot():
    # Download and Preprocess Data
    sequences, metadata = load_sequence_and_metadata()
    metadata['Year'] = metadata['Collection Date'].apply(lambda x: x.year)
    metadata = metadata[metadata['Host Species'] == 'IRD:Human']
    gb = metadata.groupby('Year').count().reset_index()
    logger.debug('loaded and preprocessed sequences per year plot data')

    # Configure Bokeh Plot
    seqperyear_src = ColumnDataSource(gb)
    hover_tool = HoverTool()
    hover_tool.tooltips = [
        ("Year", "@Year"),
        ("Num. Sequences", "@Name")
    ]
    tools = [PanTool(), CrosshairTool(), hover_tool, ResetTool()]

    p = figure(plot_width=350, plot_height=200,
               tools=tools)
    p.line(x='Year', y='Name', source=seqperyear_src)
    p.circle(x='Year', y='Name', source=seqperyear_src)
    p.xaxis.axis_label = 'Year'
    p.yaxis.axis_label = 'Number of Sequences'

    meta = dict()
    meta['n_seqs'] = len(metadata)
    meta['min_year'] = min(metadata['Year'])
    meta['max_year'] = max(metadata['Year'])
    logger.debug('finished bokeh plot.')
    return components(p), meta


def make_coordinate_scatterplot(coords, src, predcoords):
    """
    This makes one embedding coordinate scatter plot.
    """
    cx, cy = coords
    assert cx != cy

    p = figure(webgl=True, plot_height=300, plot_width=300,
               tools='pan,box_select,box_zoom,reset')
    p.scatter(x='coords{0}'.format(cx),
              y='coords{0}'.format(cy),
              color='palette', source=src)
    dim1 = 'coords{0}'.format(cx)
    dim2 = 'coords{0}'.format(cy)

    for (mpl_color, hex_color), dat in \
            predcoords.groupby(['matplotlib_colors', 'hexdecimal_colors']):
        d = dat[[dim1, dim2]]
        if len(d) >=10:
            hull = ConvexHull(d[[dim1, dim2]])
            for simplex in hull.simplices:
                p.circle(d.iloc[simplex][dim1], d.iloc[simplex][dim2],
                         fill_color=hex_color)
                p.line(d.iloc[simplex][dim1], d.iloc[simplex][dim2],
                       line_color=hex_color)

    p.xaxis.axis_label = 'Dimension {0}'.format(cx + 1)
    p.yaxis.axis_label = 'Dimension {0}'.format(cy + 1)

    return p


def make_coord_plots():
    """
    This makes all of the embedding coordinate scatter plots.
    """
    data = pd.read_csv('https://raw.githubusercontent.com/ericmjl/flu-sequence-predictor/master/data/metadata_with_embeddings.csv',  # noqa
                       index_col=0, parse_dates=['Collection Date'])
    data = data.set_index('Collection Date').resample('Q').mean()
    palette = inferno(len(data))
    data['palette'] = palette

    src = ColumnDataSource(data)

    predcoords = load_prediction_coordinates()

    p1 = make_coordinate_scatterplot([0, 1], src, predcoords)
    p2 = make_coordinate_scatterplot([1, 2], src, predcoords)
    p2.x_range = p1.y_range
    p3 = make_coordinate_scatterplot([0, 2], src, predcoords)
    p3.x_range = p1.x_range
    p3.y_range = p2.y_range

    r1 = row(p1, p2, p3)

    evo_script, evo_div = components(r1)

    return evo_script, evo_div
