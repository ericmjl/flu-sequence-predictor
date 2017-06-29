--------

Good morning everybody. My name is Eric, and I am thrilled to present Flu Forecaster, a project aiming to forecast influenza sequence evolution using machine learning.

--------

Forecasting flu evolution is an important business problem to solve. Vaccines are a life-saving public health tool that also happens to be worth $4B annually. However, historical vaccine efficacy has never exceeded 60%. **Underperforming flu vaccines risk undermining public trust in this valuable tool.**

--------

From a scientific perspective, part of the problem is how vaccine strains are chosen. Vaccine seed strains are selected months to years in advance of their actual deployment. In this time window, the flu virus may have evolved. If instead we forecast what flu will look like, we may be able to pre-emptively manufacture the vaccines that are actually needed at the time of deployment.

------

From a technical perspective, forecasting sequence evolution is difficult. Here's why. Firstly, we encounter a "combinatorial explosion" problem. With 20 possible amino acids possible at each position, as protein length increases, the total number of possible sequences increases exponentially - note the log scale on the Y-axis. In addition, there's no notion of "forward momentum" with time. For example, a protein sequence can start with the letter D, mutate to Q, and mutate back to D. We can't assign a "directionality" to these mutations.

If we were able to transform our problem into a continuous regression one, perhaps then we'd be able to borrow tools from that space instead.

---

This can be accomplished using variational autoencoders. For the purposes of this talk, consider them to be the "translator" between discrete and continuous representations of data. Let me show you how it's used in this project.

---

We start first with time-stamped influenza protein sequences. They are converted first into a binary format, through a one-of-K encoding.

---

This binary matrix is then passed through a variational autoencoder, yielding a...

---

...continuous representation of sequences. Now, we can apply time-series regression tools to the problem. Here, Gaussian process regression powers Flu Forecaster's predictions, yielding a probability distribution over forecasted space.

---

We can then pass the coordinates back through the variational autoencoder, yielding reconstructed protein sequences. Note that the uncertainty over forecasted space is expressed not as a single forecasted sequence, but a set of sequences, each with a likelihood score.

---

This set of forecasted sequences can then be synthesized as a library of DNA, which can be stockpiled ahead-of-time for production.

---

This project involves time-series regression, and so back-testing is the validation method of choice. Here, we held out two calendar quarters of data, which are the red dots, and check to see that they fall within the model predictions, which is the thick yellow band, and indeed they do.

Those red dots represent a sequence, and amongst the forecasted sequences, we can check their associated likelihood score - and it turns out they’re highly ranked at the number 2 position.

---

To learn more about the project, you can come to fluforecaster.herokuapp.com. In it, I make predictions on the coming two calendar quarters as a multiple sequence alignment. The sequences are ordered from most likely to show up at the top to least likely at the bottom, and you can scroll left-to-right to see which positions are forecasted to have high variability.

---

Alright, some conclusions here.

Firstly, sequence evolution forecasting is a hard problem.

However, if we convert the data representation to a continuous one, then maybe we can make it an easier problem.

Finally, creative chaining of deep learning tools may give us a way to tackle hard problems.

---

With that, I'd like to thank you for your time. A little bit about myself: I just finished graduate school at MIT in Biological Engineering, I am an avid proponent of open source because it's the right thing to do, and I love playing the bass because of the bassist's philosophy: do really important things behind the limelight, but step up into the spotlight when needed. I also like sailing, because my wife asked to learn it :).
