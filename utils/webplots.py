from bokeh.layouts import row
from bokeh.plotting import figure
from bokeh.palettes import inferno
from bokeh.models import (ColumnDataSource, Range1d, PanTool, HoverTool,
                          ResetTool, CrosshairTool)
from bokeh.embed import components
from utils.data import load_sequence_and_metadata, load_prediction_coordinates
from scipy.spatial import ConvexHull
from collections import defaultdict
import pandas as pd
import logging
from datetime import datetime
import yaml



def make_vaccine_effectiveness_plot():
    """
    This makes the plot that introduces vaccine effectiveness.
    """
    # Download and preprocess data.
    starttime = datetime.now()
    cdc_tables = pd.read_html('https://www.cdc.gov/flu/professionals/vaccination/effectiveness-studies.htm')  # noqa
    cdc_ve = cdc_tables[0]
    cdc_ve.columns = cdc_ve.loc[0, :]
    cdc_ve = cdc_ve.drop(0).reset_index(drop=True)
    cdc_ve.columns = ['season', 'reference', 'study_sites', 'num_patients',
                  'overall_ve', 'CI']
    cdc_ve['season_start'] = cdc_ve['season'].str.split('-').str[0]\
        .apply(lambda x: str(x))
    # print('downloaded and preprocessed vaccine effectiveness data.')

    # Configure Bokeh Plot
    cdc_src = ColumnDataSource(cdc_ve)
    hover_tool = HoverTool()
    hover_tool.tooltips = [
        ("Year", "@season_start"),
        ("Effectiveness (%)", "@overall_ve")
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
    endtime = datetime.now()
    elapsed = endtime - starttime
    print(f'make_vaccine_effectiveness_plot() took {elapsed} seconds')
    return components(p)


def make_num_sequences_per_year_plot():
    starttime = datetime.now()
    # Download and Preprocess Data
    sequences, metadata = load_sequence_and_metadata()
    metadata['Year'] = metadata['Collection Date'].apply(lambda x: x.year)
    metadata = metadata[metadata['Host Species'] == 'IRD:Human']
    gb = metadata.groupby('Year').count().reset_index()

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
    endtime = datetime.now()
    elapsed = endtime - starttime
    print(f'make_num_sequences_per_year_plot() took {elapsed} seconds.')
    return components(p), meta


def make_coordinate_scatterplot(coords, src, predcoords, vacc_src):
    """
    This makes one embedding coordinate scatter plot.
    """
    starttime = datetime.now()
    cx, cy = coords
    assert cx != cy

    p = figure(webgl=True, plot_height=300, plot_width=300,
               tools='pan,box_select,wheel_zoom,reset')

    # Plot the "average coordinates per quarter.".
    p.scatter(x='coords{0}'.format(cx),
              y='coords{0}'.format(cy),
              color='palette', source=src,
              name='avg')

    # Plot the vaccine strains.
    p.square(x='coords{0}'.format(cx),
             y='coords{0}'.format(cy),
             color='blue',
             line_color="black",
             name="vacc",
             source=vacc_src)

    # Add the hover tool for only the vaccine plot (name="vacc")
    hover_vacc = HoverTool(names=["vacc"])
    hover_vacc.tooltips = [("Vaccine, Years Deployed", "@years_deployed"),]
    p.add_tools(hover_vacc)

    hover_avg = HoverTool(names=['avg'])
    hover_avg.tooltips=[("Average Sequence, Year", "@year")]
    p.add_tools(hover_avg)

    dim1 = 'coords{0}'.format(cx)
    dim2 = 'coords{0}'.format(cy)

    xs_all = []
    ys_all = []
    colors = []
    for (mpl_color, hex_color), dat in\
            predcoords.groupby(['matplotlib_colors', 'hexdecimal_colors']):
        d = dat[[dim1, dim2]]

        if len(d) >=10:
            xs = []
            ys = []
            hull = ConvexHull(d[[dim1, dim2]])
            for v in hull.vertices:
                xs.append(d.iloc[v][dim1])
                ys.append(d.iloc[v][dim2])
            xs.append(xs[0])
            ys.append(ys[0])
            xs_all.append(xs)
            ys_all.append(ys)
            colors.append(hex_color)
    p.multi_line(xs_all, ys_all, color=colors)

    p.xaxis.axis_label = 'Dimension {0}'.format(cx + 1)
    p.yaxis.axis_label = 'Dimension {0}'.format(cy + 1)
    endtime = datetime.now()
    elapsed = endtime - starttime
    print(f'make_coordinate_scatterplot() took {elapsed} seconds.')
    return p


def make_coord_plots():
    """
    This makes all of the embedding coordinate scatter plots.
    """
    # Read in the data.
    data = pd.read_csv('https://raw.githubusercontent.com/ericmjl/flu-sequence-predictor/master/data/metadata_with_embeddings.csv',  # noqa
                       index_col=0, parse_dates=['Collection Date'])

    data['year'] = data['Collection Date'].apply(lambda x: x.year)

    # Filter out just vaccine strains.
    with open('data/vaccine_strains.yaml', 'r+') as f:
        vaccine_strains = yaml.load(f)
    vacc_data = data[data['Strain Name'].isin(vaccine_strains.values())]
    vacc_data.drop_duplicates(subset=['Strain Name'], inplace=True)
    vacc_data['years_deployed'] = 0
    vaccine_strains_by_name = defaultdict(list)
    for year, strain in vaccine_strains.items():
        vaccine_strains_by_name[strain].append(year)
    vacc_data['years_deployed'] = vacc_data['Strain Name'].apply(lambda x: vaccine_strains_by_name[x])
    vacc_src = ColumnDataSource(vacc_data)

    # Resample data to quarterly data.
    data = data.set_index('Collection Date').resample('Q').mean()
    palette = inferno(len(data))
    data['palette'] = palette


    src = ColumnDataSource(data)

    predcoords = load_prediction_coordinates()

    p1 = make_coordinate_scatterplot([0, 1], src, predcoords, vacc_src)
    p2 = make_coordinate_scatterplot([1, 2], src, predcoords, vacc_src)
    p2.x_range = p1.y_range
    p3 = make_coordinate_scatterplot([0, 2], src, predcoords, vacc_src)
    p3.x_range = p1.x_range
    p3.y_range = p2.y_range

    r1 = row(p1, p2, p3)

    evo_script, evo_div = components(r1)

    return evo_script, evo_div
