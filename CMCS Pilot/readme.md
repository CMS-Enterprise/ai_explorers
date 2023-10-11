README

T-MSIS ML Pilot -- Files Explainer

This machine-learning pilot project was conducted within the CMS Data
Connect Databricks virtual private cloud (VPC+), prior to it being moved
to E2++ in the summer 2023) environment using native Databricks
notebooks.

To facilitate knowledge sharing for those both inside and outside of the
Databricks environment, each of the core four native notebooks were
exported in all the options available:

1.  .dbc: Native Databricks archive file that can be imported directly
    into Databricks.

2.  .py: 'Source file' export option creates a standard python text
    file.

3.  .ipynb: IPython export supports rich python-based formatting.

4.  .html: self-explanatory.

Description of the Four Notebooks

1.  T-MSIS Pilot Final LR -- Single Model

    a.  This notebook is the base case ML using only standard python
        library linear regression for a single state/territory per run.

2.  T-MSIS Pilot Final -- LR -- Single Model -- All States

    a.  This notebook is the same as above but loops through all 54
        states and territories per run.

3.  T-MSIS Pilot Final LR -- Auto Multi-Model

    a.  This notebook utilizes the Databricks built-in AutoML+++
        library, linear regression option for a single state/territory
        per run.

4.  T-MSIS Pilot Final -- FC -- Auto Multi-Model

    a.  This notebook utilizes the Databricks built-in AutoML+++
        library, forecasting option for a single state/territory per
        run.

See the posted T-MSIS ML Pilot related documents for details regarding
the advantages, disadvantages, and caveats for each of the approaches
above and the limitations the now legacy VPC environment imposed on the
project.

\+ Databricks VPC - See this link for background:
<https://docs.databricks.com/en/administration-guide/cloud-configurations/aws/customer-managed-vpc.html>

++ Databricks E2 -- See this link for background:
<https://docs.databricks.com/en/getting-started/overview.html#control-plane-and-data-plane>

+++ AutoML -- See this link for details on how Databrick's
implementation of AutoML works:
<https://docs.databricks.com/en/machine-learning/automl/index.html>
