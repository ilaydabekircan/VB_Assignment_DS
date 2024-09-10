#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from kmodes.kprototypes import KPrototypes
import matplotlib.pyplot as plt


# In[2]:


# import clean dataframe with customer information
# path_to_csv = '/Users/ilaydabekircan/Documents/Vision_Bridge/DS_Assignment'
# pd.read_csv(path_to_csv)

path = '/Users/ilaydabekircan/Documents/Vision_Bridge/DS_Assignment/py_files'

csv_files = [file for file in os.listdir(path) if file.endswith('.csv')]

for file in csv_files:
    df_name = file.split('.')[0]
    globals()[df_name] = pd.read_csv(os.path.join(path, file))

df_clean.head(3)


# In[3]:


df_clean.info()


# CustomerID should not be in the dataset while clustering. Otherwise, the clustering algorithm will take it as a numerical column while the numeric information of customer identification is not important and it is only used as a key. Therefore, CustomerID is set as index.

# In[4]:


df_clean.set_index('CustomerID', inplace = True)


# KPrototypes clustering method can use both numerical and categorical data but we need to give the categorical columns as an argument to define them into the clustering.

# In[5]:


# define an array with categorical columns' indexes
cat_cols = ['CustomerCity', 'CustomerState', 'Gender', 'Age', 'EmploymentStatus', 'Education', 'Occupation', 'Industry', 'MainCategoryMode',
           'SubCategoryMode', 'TypeMode']

cat_col_indices = [df_clean.columns.get_loc(col) for col in cat_cols]
cat_col_indices


# In[6]:


# run KPrototypes from 1 to 10 clusters

# costs = []
# k = range(1,11)

# for i in k:
#     kp = KPrototypes(n_clusters = i, 
#                      init = 'Cao', 
#                      n_init = 3, 
#                      verbose = 1)
    
#     kp.fit(df_clean, 
#            categorical = cat_col_indices)
    
#     costs.append(kp.cost_)


# In[7]:


# plot the clusters for elbow method
# plt.figure(figsize=(8, 5))
# plt.plot(k, 
#          costs, 
#          'ro-', 
#          markersize = 8)
# plt.xlabel('Number of Clusters (k)')
# plt.ylabel('Cost')
# plt.title('Elbow Method for Optimal k')
# plt.show()


# We use elbow method to decide which cluster number we should choose. Since there is an elbow at k=3, we proceed with 3 clusters.

# In[29]:


kp = KPrototypes(n_clusters = 3, 
                 init = 'Cao', 
                 n_init = 3, 
                 verbose = 1)

clusters = kp.fit_predict(df_clean, 
                          categorical = cat_col_indices)


# In[31]:


# define cluster for each customer
# add 1 to get rid of index numbers (1,2,3 instead of 0,1,2)
df_clean['Segment'] = clusters + 1


# In[33]:


df_clean['Segment'].value_counts()


# In[43]:


path = '/Users/ilaydabekircan/Documents/Vision_Bridge/DS_Assignment/py_files/df_segment.csv'
df_clean.to_csv(path, index = False)

