# Flu Forecaster

An experimental deep learning &amp; genotype network-based system for predicting new influenza protein sequences.

## Rationale

Flu Forecaster was first fully developed during my time as an Insight Health Data Fellow. The projected business use case is to predict what future strains of flu will look like, which would thus help inform the pre-emptive development of vaccines. No longer would we have to select currently-circulating strains; instead, we could forecast what strains would look like 6 months down the road, pre-emptively synthesize them (using synthetic biology methods), and rapidly scale up production of the ones used for the flu shot vaccine.

## Getting Started

### Viewing Flu Forecaster

Flu Forecaster is hosted on [Heroku][heroku], but can also be hosted locally. An internet connection is required for the display components and for downloading data from this GitHub repository.

[heroku]: https://fluforecaster.herokuapp.com

### Developing Flu Forecaster

To develop Flu Forecaster, it is recommended that you have access to a GPU.

## Architecture

Flu Forecaster's dashboard is written using [Flask][flask], [Bokeh][bokeh] and [pandas][pandas].

[flask]: http://flask.pocoo.org/
[bokeh]: http://bokeh.pydata.org/
[pandas]: http://pandas.pydata.org/

Flu Forecaster's back-end is powered by Jupyter notebooks that use machine learning algorithms implemented in [Keras][keras] and [PyMC3][pymc3].

Keras is used for the variational autoencoders, which learn a continuous, lower dimensional, and latent embedding of influenza protein sequence space, and can generate new sequences from that space.

PyMC3 is used for gaussian process regression, which allows us to model arbitrary time-varying functions, thus providing a way to forecast where (in the latent space) influenza is evolving towards. Once we have those forecasted latent space coordinates, we can decode them back into protein sequences.

[keras]: https://keras.io/
[pymc3]: https://github.com/pymc-devs/pymc3

## Science

### Flu Biology

Behind all of this is some real influenza biology. Influenza evolves under evolutionary pressure, arising from our immune systems, vaccines, drug treatments, and possibly more pressure sources not mentioned here. The process of evolution essentially results in taking currently-circulating viruses, weeding out those that are "unfit", and making new viruses based on currently-circulating ones. Thus, current strains are the substrate for future strains.

### Forecasting Evolution with VAEs & GPs

Yet, when we talk about "sequences", there's no notion of "direction". Who's to say that the mutation of one position from a K to an L is moving "forward" in time? An alternative is to learn vectors in continuous space. This is why we use a variational autoencoder (VAE). The VAE translates the discrete representation of our sequence data (a one-of-K encoding of amino acids at each position) into a continuous, "latent" representation.

Once we're in the latent representation, then we can train a Gaussian Processes (GPs) regression model on the data and use it to make extrapolations.
