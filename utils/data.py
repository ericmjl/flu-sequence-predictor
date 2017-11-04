import logging
from datetime import datetime

import pandas as pd
from Bio import SeqIO

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def load_sequence_and_metadata(kind='feather'):
    """
    Returns the sequences as a list of SeqRecords, and metadata as a pandas
    DataFrame.
    """
    starttime = datetime.now()
    sequences = [s for s
                 in SeqIO.parse('data/20170531-H3N2-global.fasta', 'fasta')
                 ]
    if kind == 'csv':
        metadata = pd.read_csv('data/20170531-H3N2-global.tsv',
                               sep='\t',
                               parse_dates=['Collection Date'])
    elif kind == 'feather':
        metadata = pd.read_feather('data/20170531-H3N2-global.feather')
    endtime = datetime.now()
    elapsed = endtime - starttime
    print(f'load_sequence_and_metadata() took {elapsed} seconds.')
    return sequences, metadata


def load_prediction_coordinates():
    """
    Returns the coordinates of the predictions, and their associated colours,
    as a pandas DataFrame.
    """
    logger.debug('started load_prediction_coordinates()')
    df = pd.read_csv('data/oneQ_prediction_coords_with_colors.csv',
                     index_col=0)
    logger.debug('finished load_prediction_coordinates()')
    return df
