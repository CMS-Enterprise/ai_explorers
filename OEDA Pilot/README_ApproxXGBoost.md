# XGBoost Tree Approximator

This README file describes the contents and use of the XGBoost Tree Approximator
experiments conducted as part of the OEDA AI Explorers pilot project. This
README applies to the XGBoostApprox notebook originally developed in the
CCW VRDC environment, as well as the FBT notebook, and depends on the data 
tables and resources deployed there.

## Tree Approximator Code

The XGBoost Tree Approximator is an implementation of the method of 
[Sagi and Rokach, 2021](https://doi.org/10.1016/j.ins.2021.05.055), and
the library is minimally adapted from the original code published on 
GitHub at [`sagyome/XGBoostTreeApproximator`](https://github.com/sagyome/XGBoostTreeApproximator), 
in order to run in the VRDC Databricks environment without importing as library (due to security restrictions). The adaptation consists primarily
of structuring the contents of the constituent files into notebook cells,
eliminating imports and adjusting ordering as necessary to load correctly.

The primary interface to the library is the `FBT` ("Forest-Based Tree") 
class, which is imported into this notebook by the cell that runs the 
FBT notebook.

## Loading Data and Training a Classifier

The next set of cells load a dataset and train an XGBoost model on it.
In this notebook, the parameters are simply chosen as reasonable
defaults, as the actual performance of the exact model was not
the primary interest here. The exact model is a straightforward XGBoost
model, and all the metrics and analysis applied to the full
baseline models could be applied to it as well.

To avoid having to constantly retrain this model, we also save it into
a Python pickle file, so that we can restart the notebook later from
this point.

## Training the XGBoost Tree Approximator

We now train an FBT approximator on the exact model. As noted in the
worksheet, this is an extremely compute-intensive process that will
easily take upwards of 15 hours to run. (For this reason, we did not
spend time assessing the effect of different parameter settings for
the FBT model.)

We also save the trained FBT model as a pickle file and then compress
it using the bzip2 algorithm. This cuts the size of the model on disk by
approximately 90%, the most important impact of which is a dramatic
speedup in future loading time.

## Comparisons

The remaining cells demonstrate comparing the performance of the exact
and approximate models. Broadly speaking, the FBT model performs somewhat
worse, but given the poor performance of the XGBoost models in general
in this case, it is difficult to draw any meaningful inferences about
the relative strengths and weaknesses of the approximate model.