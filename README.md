# Context Tree Weighting Algo Application

This is a project I worked on during my graduation intern of my master's degree.

Financial markets operates, during their opening hours, on a continuous, high frequency basis. The advent of high-frequency data sets makes it possible to capture the characteristics of the market promptly. As the high-frequency data is massive, it’s of great importance to extract the useful information from them. We are therefore interested in a modeling technique frequently used in data compression.

This is the application of Context Tree theory to Bayesian inferences. The inferences assume that the phenomena are Markovian. The algorithms therefore only apply to Markov chains (or Hidden Markov Chain). Markov chains are a classic modeling of different physical phenomena such as stock market price. They are characterized by discretized states and probabilities of transitions between the past state and the future state. But in reality, we do not have access to these data. The idea is then to identify the structure of the Markov tree and its transition probabilities, using the observations of the system we have. To do so we use the Context Tree Weighting algorithm. This one allows an exponential reduction of the number of coefficients to be considered, by eliminating the non useful transition probabilities. We apply the method to the intraday stock index future data and try to identify the market pattern behind them.

