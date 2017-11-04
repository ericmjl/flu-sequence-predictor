import logging
from logging.handlers import RotatingFileHandler

from Bio import SeqIO
from bokeh.resources import INLINE
from flask import Flask, render_template

from utils.webplots import (make_coord_plots, make_num_sequences_per_year_plot,
                            make_vaccine_effectiveness_plot)

app = Flask(__name__)


@app.route('/')
def home():

    ve_script, ve_div = make_vaccine_effectiveness_plot()
    (nseq_script, nseq_div), (nseq_metadata) = \
        make_num_sequences_per_year_plot()
    evo_script, evo_div = make_coord_plots()
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    seqs = [s for s in SeqIO.parse('data/twoQ_predictions.fasta', 'fasta')]
    n_seqs = len(seqs)

    return render_template('index.html', js_resources=js_resources,
                           css_resources=css_resources,
                           evo_script=evo_script, evo_div=evo_div,
                           nseq_script=nseq_script, nseq_div=nseq_div,
                           nseq_metadata=nseq_metadata,
                           n_seqs=n_seqs, ve_script=ve_script, ve_div=ve_div)


if __name__ == '__main__':
    app.run(debug=True)
