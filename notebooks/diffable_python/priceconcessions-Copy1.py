# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all
#     notebook_metadata_filter: all,-language_info
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# ## Trends of antidepressant prescribing since 2016

import os
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import seaborn as sns
from matplotlib.dates import  DateFormatter
# %matplotlib inline
from ebmdatalab import bq
from ebmdatalab import charts
from ebmdatalab import maps

# The Lancet Psychiatry published a [recent analysis using openly available NHS prescribing data](https://www.thelancet.com/journals/lanpsy/article/PIIS2215-0366(20)30530-7/fulltext) to measure the rate of antidepressant prescribing in England during the first wave of the pandemic. Armitage found a 3.9% increase in antidepressant prescribing during April to September 2020, compared to the same period a year earlier.
#
# The author strongly implies that this change is due to the pandemic: “These data suggest the predictions that mental health would be severely affected by COVID-19 were correct. They also indicate that this increased burden of mental ill-health is being disproportionately managed by pharmacological treatments in primary care...” 
#
# Is this level of of increase correct, and how does it compare to previous years?

# ### Import data from BigQuery

# To understand the increases, we import data from BigQuery using the same methodology as Armitage, i.e. compare the number of items prescribed between April and September in two consecutive years.

# +
#import data from bigquery for antidepressants
sql = """
SELECT 
SUM (CASE when month between '2016-04-01' and '2016-09-01' THEN items  else 0 END) as items_2016, #items from April-September 2016
SUM (CASE when month between '2017-04-01' and '2017-09-01' THEN items  else 0 END) as items_2017, #items from April-September 2017
SUM (CASE when month between '2018-04-01' and '2018-09-01' THEN items  else 0 END) as items_2018, #items from April-September 2018
SUM (CASE when month between '2019-04-01' and '2019-09-01' THEN items  else 0 END) as items_2019, #items from April-September 2019
SUM (CASE when month between '2020-04-01' and '2020-09-01' THEN items  else 0 END) as items_2020, #items from April-September 2020
ROUND(100* (IEEE_DIVIDE(SUM(CASE WHEN month between '2017-04-01' AND '2017-09-01' THEN items ELSE 0 END), (SUM (CASE WHEN month between '2016-04-01' and '2016-09-01' THEN items  ELSE 0 END)))-1),2) as perc_increase_2017, #calculates percentage difference between April-September 2016 and April-September 2017
ROUND(100* (IEEE_DIVIDE(SUM(CASE WHEN month between '2018-04-01' AND '2018-09-01' THEN items ELSE 0 END), (SUM (CASE WHEN month between '2017-04-01' and '2017-09-01' THEN items  ELSE 0 END)))-1),2) as perc_increase_2018, #calculates percentage difference between April-September 2017 and April-September 2018
ROUND(100* (IEEE_DIVIDE(SUM(CASE WHEN month between '2019-04-01' AND '2019-09-01' THEN items ELSE 0 END), (SUM (CASE WHEN month between '2018-04-01' AND '2018-09-01' THEN items  ELSE 0 END)))-1),2) as perc_increase_2019, #calculates percentage difference between April-September 2018 and April-September 2019
ROUND(100* (IEEE_DIVIDE(SUM(CASE WHEN month between '2020-04-01' AND '2020-09-01' THEN items ELSE 0 END), (SUM (CASE WHEN month between '2019-04-01' AND '2019-09-01' THEN items  ELSE 0 END)))-1),2)as perc_increase_2020 #calculates percentage difference between April-September 2019 and April-September 2020
FROM ebmdatalab.hscic.normalised_prescribing
WHERE
bnf_code LIKE '0403%' #section 4.3 of legacy BNF - all antidepressants
"""

exportfile = os.path.join("..","data","adp_df.csv") #set path for data cache
adp_df = bq.cached_read(sql, csv_path=exportfile, use_cache=True) #save dataframte to csv
display(adp_df) #show dataframe as a table
# -

# As we can see from above, the author is correct that there has been an increase of approximately 3.9% between the six months to September 2020, and the same period the year before.  However, this is a lower increase that in 2018 and 2019 (4.79% and 6.07%) and similar to the 2017 increase (3.80%).

# ### Restricting to Selective Seretonin Reuptake Inhibitors (SSRIs)

# The legacy BNF for antidepressants includes drugs, such as amitryptyline and nortryptyline, which are now more commonly used for other conditions (such as pain in the case of amitryptyline).  In order to more accurately assess the uptake of antidepressants for mental health issues, it would be worth using only section 4.3.3 (SSRIs) as a useful indicator, as these a)are the most commonly used drug, b) tend only to be used primarily for mental health issues.

# +
#import data from bigquery for SSRIs only
sql = """
SELECT 
SUM (CASE when month between '2016-04-01' and '2016-09-01' THEN items  else 0 END) as items_2016, #items from April-September 2016
SUM (CASE when month between '2017-04-01' and '2017-09-01' THEN items  else 0 END) as items_2017, #items from April-September 2017
SUM (CASE when month between '2018-04-01' and '2018-09-01' THEN items  else 0 END) as items_2018, #items from April-September 2018
SUM (CASE when month between '2019-04-01' and '2019-09-01' THEN items  else 0 END) as items_2019, #items from April-September 2019
SUM (CASE when month between '2020-04-01' and '2020-09-01' THEN items  else 0 END) as items_2020, #items from April-September 2020
ROUND(100* (IEEE_DIVIDE(SUM(CASE WHEN month between '2017-04-01' AND '2017-09-01' THEN items ELSE 0 END), (SUM (CASE WHEN month between '2016-04-01' and '2016-09-01' THEN items  ELSE 0 END)))-1),2) as perc_increase_2017, #calculates percentage difference between April-September 2016 and April-September 2017
ROUND(100* (IEEE_DIVIDE(SUM(CASE WHEN month between '2018-04-01' AND '2018-09-01' THEN items ELSE 0 END), (SUM (CASE WHEN month between '2017-04-01' and '2017-09-01' THEN items  ELSE 0 END)))-1),2) as perc_increase_2018, #calculates percentage difference between April-September 2017 and April-September 2018
ROUND(100* (IEEE_DIVIDE(SUM(CASE WHEN month between '2019-04-01' AND '2019-09-01' THEN items ELSE 0 END), (SUM (CASE WHEN month between '2018-04-01' AND '2018-09-01' THEN items  ELSE 0 END)))-1),2) as perc_increase_2019, #calculates percentage difference between April-September 2018 and April-September 2019
ROUND(100* (IEEE_DIVIDE(SUM(CASE WHEN month between '2020-04-01' AND '2020-09-01' THEN items ELSE 0 END), (SUM (CASE WHEN month between '2019-04-01' AND '2019-09-01' THEN items  ELSE 0 END)))-1),2)as perc_increase_2020 #calculates percentage difference between April-September 2019 and April-September 2020
FROM ebmdatalab.hscic.normalised_prescribing
WHERE
bnf_code LIKE '040303%' #paragraph 4.3.3 of legacy BNF - SSRIs
"""

exportfile = os.path.join("..","data","ssri_df.csv") #set path for data cache
ssri_df = bq.cached_read(sql, csv_path=exportfile, use_cache=True) #save dataframte to csv
display(ssri_df) #show dataframe as a table

# + [markdown]
# As can be seen above, the increase between the six months to September 2020 compared with the same period the previous year is the lowest of the 4 years analysed.
# -



