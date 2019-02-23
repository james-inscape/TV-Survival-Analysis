   
import boto
import boto3
import pandas as pd
import sys
import numpy as np
from boto.s3.connection import S3Connection
import psycopg2 as ps
from psycopg2.extensions import AsIs
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches #for custom legends
import seaborn as sns
from lifelines import KaplanMeierFitter #survival analysis library
from lifelines.statistics import logrank_test #survival statistical testing
from IPython.display import Image
from IPython.core.display import HTML



user = 'jamesm'
password = '=783r+GcF?Mujf4Y'
host='prod-redshift-warm-live.czgvytlrzgbu.us-east-1.redshift.amazonaws.com'
port='5439'
database='detectionlive'

connection = ps.connect(user=user,
                        password=password,
                        host=host,
                        port=port,
                        database=database)

cursor = connection.cursor()

sql = '''
select * from jamesm.tv_survival8;
'''

cursor.execute(sql)

seg_pre = cursor.fetchall()
    
tv_survival = pd.DataFrame.from_records(seg_pre)
tv_survival.columns =['tvid', 'tv_active', 'tv_dob', 'curr_max_session_start', 'curr_min_session_start','prev_max_session_start', 'months_elapsed', 'sigma', 'mseries', 'other']

tv_survival_work = tv_survival

#Refactor the Event column - TV Deactivation is the Death Event
tv_survival_work["tv_inactive"] = tv_survival_work.tv_active.apply(lambda x: 1 if x == "No" else 0) #recode tv_active var

tv_survival_work.tv_active.value_counts()
tv_survival_work.tv_inactive.value_counts()


T = tv_survival_work['months_elapsed']          #Duration
E = tv_survival_work['tv_inactive']             #Event

kmf = KaplanMeierFitter()

kmf.fit(T, event_observed=E)  # or, more succinctly, kmf.fit(T, E)


kmf.survival_function_
#Print the Event Table
kmf.event_table
#The removed column contains the number of observations removed during that time period, whether due to death (the value in the observed column) 
#or censorship. So the removed column is just the sum of the observed and censorship columns. The entrance column tells us whether any 
#new TVs entered the population at that time period. Since all TVs start at time=0 
#the entrance value is Nmillion at that time and 0 for all other times.

#The at_risk column contains the number of TVs that are still active during a given time. 
#The value for at_risk at time=0, is just equal to the entrance value. For the remaining time periods, 
#the at_risk value is equal to the difference between the time previous period's at_risk value and removed value, 
#plus the current period's entrance value.

kmf.plot()
# Add title and y-axis label
#plt.title("The Kaplan-Meier Estimate for TV Lifetime")
plt.title("Probability a TV is still active - /n Death is defined as no activity in last 12 months")
plt.show()


#Now plot inactive only
inactive = tv_survival_work.query('tv_inactive == 1')


TI = inactive['months_elapsed']          #Duration
EV = inactive['tv_inactive']             #Event

kmf = KaplanMeierFitter()
kmf.fit(TI, event_observed=EV)  # or, more succinctly, kmf.fit(T, E)
kmf.plot()
# Add title and y-axis label
#plt.title("The Kaplan-Meier Estimate for TV Lifetime")
plt.show()
kmf.event_table


#Now fit groups - MSeries
groups = tv_survival_work['mseries']
ix = (groups == 1)

kmf.fit(T[~ix], E[~ix], label='All TVs')
ax = kmf.plot()

kmf.fit(T[ix], E[ix], label='MSeries')
ax = kmf.plot(ax=ax)
plt.show()


#Now fit groups - Sigma
groups = tv_survival_work['sigma']
ix = (groups == 1)

kmf.fit(T[~ix], E[~ix], label='All TVs')
ax = kmf.plot()

kmf.fit(T[ix], E[ix], label='Sigma')
ax = kmf.plot(ax=ax)
plt.show()














