#!/usr/bin/env python
# coding: utf-8

# In[1]:


# import necessary libraries

import pandas as pd
import numpy as np
import os

# import matplotlib.pyplot as plt
# import seaborn as sns


# In[2]:


# import all datasources and convert them into pandas dataframes

path = '/Users/ilaydabekircan/Documents/Vision_Bridge/DS_Assignment/AssignmentData'

csv_files = [file for file in os.listdir(path) if file.endswith('.csv')]

for file in csv_files:
    df_name = file.split('.')[0]
    globals()[df_name] = pd.read_csv(os.path.join(path, file))


# In[3]:


# print names of each dataframe
df_names = [name for name, obj in globals().items() if isinstance(obj, pd.DataFrame)]
df_names


# # BUYERS

# In[5]:


print('Number of customers in our dataset', Customers['CustomerID'].nunique())
print('Number of customers who bought something:', Orders['CustomerID'].nunique())
print('Number of customers who didnt buy something:', Customers['CustomerID'].nunique() - Orders['CustomerID'].nunique())


# Although most of the customers didn't buy anything, we can still learn from their behaviours.

# First, we will merge only the datasets with customer and product information into CustomerBuys and the store information will be gathered under SellerSells df. In CustomerBuys, Customers df will be the main dataset and therefore left join will be used while merging other datasets into Customers.

# In[8]:


# function to define season by month
def find_season(month_num):
    if month_num in [12, 1, 2]:
        return 1
    elif month_num in [3, 4, 5]:
        return 2
    elif month_num in [6, 7, 8]:
        return 3
    elif month_num in [9, 10, 11]:
        return 4


# Customers df has only two columns with missing information.

# In[10]:


customers_na = Customers.isna().sum()
customers_na[customers_na > 0]


# Orders df has no missing information within itself.

# In[12]:


orders_na = Orders.isna().sum()
orders_na[orders_na > 0]


# Before merging Customers and Orders, both dataframes need preprocessing. Some columns in Customers are renamed to prevent confusion in later steps. Also, missing information in occupation and industry columns are labeled as 'Unknown' while the unnecessary columns are dropped. Email, phone and the data creation is unnecessary for customer segmentation purposes. Since we have CustomerID, name is also unnecessary. Country is not used in the dataset since all observations are from the US.
# 
# By using 'OrderDate' in Orders df, three features are created to show 'OrderMonth', 'OrderWeekOfMonth' and 'OrderSeason'.

# In[14]:


# rename the columns that can be also used in other datasets
Customers.rename(columns = {'City': 'CustomerCity', 'State': 'CustomerState'}, inplace=True)
# fill the missing values in Occupation and Industry columns with Unknown
Customers.fillna({'Occupation': 'Unknown', 'Industry': 'Unknown'}, inplace=True)
# drop the unnecessary columns for customer segmentation (all customers are from USA so country information is redundant)
Customers.drop(columns = ['Name', 'Email', 'Phone', 'Country', 'CreatedAt'], inplace = True)

# change the type of OrderDate column
Orders['OrderDate'] = pd.to_datetime(Orders['OrderDate'])

# create new features related to the order date 
Orders['OrderMonth'] = Orders['OrderDate'].dt.month
Orders['OrderWeekOfMonth'] = (Orders['OrderDate'].dt.day - 1) // 7 + 1
Orders['OrderSeason'] = Orders['OrderMonth'].apply(find_season)


CustomerBuys = Customers.merge(Orders, 
                               how = 'left',
                               on = 'CustomerID')
CustomerBuys.info()


# In[15]:


customerbuys_na = CustomerBuys.isna().sum()
customerbuys_na[customerbuys_na > 0]


# Not all customers buy something, so when merging Customers with Orders we have missing information for each customer without any purchase. To handle missing values, the categorical column 'Status' will be filled with Unknown string and the numerical columns will be filled with 0 for missing values. However, OrderID and OrderDate will not be filled since they will be used in later steps.

# In[17]:


CustomerBuys.fillna({'Status': 'Unknown'}, inplace = True)
CustomerBuys.fillna({'Count': 0, 'TotalAmount': 0, 'OrderMonth': 0, 'OrderWeekOfMonth': 0, 'OrderSeason': 0}, inplace=True)


# In[18]:


customerbuys_na = CustomerBuys.isna().sum()
customerbuys_na[customerbuys_na > 0]


# In[19]:


# check if there is any duplication
CustomerBuys[CustomerBuys.duplicated()].shape


# Since we have OrderID in CustomerBuys after merging with Orders, we can now merge the main df with OrderItems which give information about ProductID, price and quantity. OrderItemID is not a key since that column is not used by any other dataset. It is only used in OrderItems as index.

# In[21]:


OrderItems.head(3)


# In[22]:


OrderItems = OrderItems.drop(columns = ['OrderItemID']).rename(columns = {'Price': 'ItemPrice'})


# In[23]:


# use left join to merge OrderItems with CustomerBuys since CustomerBuys is our main dataset with customer information
CustomerBuys = CustomerBuys.merge(OrderItems, 
                                  how = 'left',
                                  on = 'OrderID')
CustomerBuys.info()


# In[24]:


# show the columns with missing values
customerbuys_na = CustomerBuys.isna().sum()
customerbuys_na[customerbuys_na > 0]


# In[25]:


# check if there is any duplication
CustomerBuys[CustomerBuys.duplicated()].shape


# In[26]:


CustomerBuys.info()


# In CustomerBuys, we have now ProductID so we can merge Products dataset to learn each product's detail such as its main category.

# In[28]:


Products.info()


# While merging datasets, some key columns (ID columns) might get null values since some customers didn't purchase anything. If an ID column has a missing value, it automatically change its type to float while it was originally integer. To prevent error while merging, we change key columns from integer to float for merging purposes.

# In[30]:


# drop unnecessary columns
# rename some columns for preventing confusion
Products = Products.drop(columns = ['CreatedAt', 'SKU']).rename(columns = {'Name': 'ProductName', 'Price': 'ProductPrice'})
Products['ProductID'] = Products['ProductID'].astype(float)
Products.drop(columns = ['RetailerID'], inplace = True)

CustomerBuys = CustomerBuys.merge(Products,
                                  how = 'left',
                                  on = ['ProductID'])


# In[31]:


CustomerBuys.head()


# Most of the customers didn't buy anything but we still want to keep them in the dataset and clustering to understand their behavior and create targeted marketings. However, we create a purchase flag to distinguish them from the customers who purchased.

# In[33]:


FlagDf = CustomerBuys.groupby('CustomerID')['TotalAmount'].sum().reset_index()
FlagDf.rename(columns = {'TotalAmount': 'PurchaseFlag'}, inplace = True)

# create a flag that if a customer purchased anything, it will give 1
FlagDf['PurchaseFlag'] = FlagDf['PurchaseFlag'].apply(lambda x: 1 if x > 0 else 0)

CustomerBuys = CustomerBuys.merge(FlagDf, 
                                  on = 'CustomerID', 
                                  how = 'left')
CustomerBuys.head(3)


# If a customer didn't purchase anything, their product information such as the columns given below should be equal to zero.

# In[35]:


CustomerBuys.loc[CustomerBuys['PurchaseFlag'] == 0, ['Count', 'TotalAmount', 'Price', 'Quantity', 'TotalPrice']] = 0
CustomerBuys.head(3)


# BehavioralData is not used because of the below example. In the main dataset (CustomerBuys), we don't have any of the CustomerID&ProductID combination shown in BehavioralData dataset. Even the observations with 'ActionType' = 'purchase' are not shown in CustomerBuys.

# In[37]:


BehavioralData


# In[38]:


BehavioralData[BehavioralData['CustomerID'] == 4456.0]


# In[39]:


CustomerBuys[CustomerBuys['CustomerID'] == 4456.0][['CustomerID', 'ProductID']]


# # SELLERS

# As mentioned earlier, store and seller information will be gathered under SellerSells df then it will be joined with CustomerBuys at the last step.

# Some dataframes keep only key identifiers and they can only be used for merging dataframes
# - **ChannelsCampaigns:** StoreID, ChannelID
# - **StoresCampaigns:** StoreID, CampaignID
# - **AudiencesCampaigns:** AudienceID, CampaignID

# In[43]:


Stores.head(3)


# In[44]:


Stores.rename(columns = {'Name': 'StoreName', 'City': 'StoreCity', 'State': 'StoreState'}, inplace=True)
Stores.drop(columns = ['Country', 'CreatedAt'], inplace = True) # only USA

SellerSells = Stores.merge(ChannelsCampaigns, 
                           how = 'left', 
                           on = 'StoreID').merge(StoresCampaigns, 
                                                 how = 'left', 
                                                 on = 'StoreID')
SellerSells.head(3)


# By adding the keys to Stores and creating SellerSells, we can now use the information in Retailers and Channels.
# 
# However, Retailers dataframe doesn't give us information about customer segmentation. (RetailerID, Name, ContactInfo, CreatedAt, UserID). 
# 
# We can only use this dataframe to use UserID as a key to merge with Users dataframe but Users also doesn't have any necessary information (UserID, Username, Email, PasswordHash, CreatedAt).
# 
# Therefore, we will only merge Channels.

# In[46]:


Channels.rename(columns = {'name': 'ChannelName'}, inplace = True)
SellerSells = SellerSells.merge(Channels.drop(columns = 'createdAt'), 
                                how = 'left', 
                                on = 'channelID')
SellerSells.head(3)


# In[47]:


SellerSells.info()


# Since we merged StoresCampaigns with Stores before, we now have CampaignID in SellerSells, which made it available for us to merge the dataset with MarketingCampaigns by using 'CampaignID'.

# In[49]:


MarketingCampaigns.head(3)


# In[50]:


MarketingCampaigns.info()


# StartDate and EndDate are object-typed but we can use them for feature engineering after changing their type to datetime.

# In[52]:


MarketingCampaigns['StartDate'] = pd.to_datetime(MarketingCampaigns['StartDate'])
MarketingCampaigns['EndDate'] = pd.to_datetime(MarketingCampaigns['EndDate'])
MarketingCampaigns.info()


# In[53]:


# All campaigns start and end at 21:50, so the time is redundant
MarketingCampaigns['StartTime'] = MarketingCampaigns['StartDate'].dt.time

# Check
MarketingCampaigns['StartTime'].sort_values() # ascending


# In[54]:


# keep only dates and remove times from StartDate and EndDate
MarketingCampaigns['StartDate'] = MarketingCampaigns['StartDate'].dt.date
MarketingCampaigns['EndDate'] = MarketingCampaigns['EndDate'].dt.date

# Reconvert to datetime
MarketingCampaigns['StartDate'] = pd.to_datetime(MarketingCampaigns['StartDate'])
MarketingCampaigns['EndDate'] = pd.to_datetime(MarketingCampaigns['EndDate'])

# Estimate how many days a campaign takes
MarketingCampaigns['CampaignDuration'] = (MarketingCampaigns['EndDate'] - MarketingCampaigns['StartDate']).dt.days
MarketingCampaigns.head(3)


# In[55]:


# All campaigns take 30 days so the duration is redundant
MarketingCampaigns[MarketingCampaigns['CampaignDuration'] != 30]


# In[56]:


# remove unnecessary columns
MarketingCampaigns = MarketingCampaigns.drop(columns = ['CreatedAt', 'StartTime', 'CampaignDuration', 'Budget'])
MarketingCampaigns['CampaignID'] = MarketingCampaigns['CampaignID'].astype(float)
MarketingCampaigns.rename(columns = {'Name': 'CampaignName'}, inplace = True)
MarketingCampaigns.head(3)


# In[57]:


SellerSells.head(3)


# In[58]:


SellerSells = SellerSells.merge(MarketingCampaigns, 
                                how = 'left',
                                on = 'CampaignID')
SellerSells.head(3)


# In[59]:


CustomerBuys.head(3)


# In[60]:


# create main df by merging customer and seller information
df = CustomerBuys.merge(SellerSells, 
                        how = 'left', 
                        on = 'RetailerID')
df.head()


# We will add a new feature to the dataframe to show if the customer make their purchase during a campaign period.

# In[62]:


# customer with CampaignFlag=1 purchased their items during the campaign period
df['CampaignFlag'] = ((df['OrderDate'] >= df['StartDate']) & (df['OrderDate'] <= df['EndDate'])).astype(int)
df[df['CampaignFlag']==1].head(3)


# In[63]:


df.info()


# In[64]:


# remove all the redundant columns for customer segmentation
df.drop(columns = ['RetailerID', 'OrderDate', 'Status', 'ProductID', 'ProductName', 'Price', 'TotalPrice', 'StoreID', 'StoreName', 
                   'StoreCity', 'StoreState', 'channelID', 'CampaignID', 'ChannelName', 'level', 'CampaignName', 'StartDate', 
                   'EndDate'], inplace = True)


# In[65]:


df.info()


# We aggregate some of the remaining columns to have only one row for each customer. For example, the most purchased main category is kept for each customer.

# In[67]:


aggregated_df = df.groupby('CustomerID').agg(
    CustomerCity = ('CustomerCity', 'first'),
    CustomerState = ('CustomerState', 'first'),
    Gender = ('Gender', 'first'),
    Age = ('Age', 'first'),
    EmploymentStatus = ('EmploymentStatus', 'first'),
    Education = ('Education', 'first'),
    Occupation = ('Occupation', 'first'),
    Industry = ('Industry', 'first'),
    Income = ('Income', 'first'),
    OrderCount = ('OrderID', 'count'),
    OrderItemMean = ('Count', 'mean'),
    TotalAmountMax = ('TotalAmount', 'max'),
    TotalAmountMin = ('TotalAmount', 'min'),
    OrderMonthMode = ('OrderMonth', lambda x: x.mode()[0] if not x.mode().empty else np.nan),
    OrderWeekOfMonthMode = ('OrderWeekOfMonth', lambda x: x.mode()[0] if not x.mode().empty else np.nan),
    OrderSeasonMode = ('OrderSeason', lambda x: x.mode()[0] if not x.mode().empty else np.nan),
    ItemPriceMean = ('ItemPrice', 'mean'),
    MainCategoryMode = ('MainCategory', lambda x: x.mode()[0] if not x.mode().empty else np.nan),
    SubCategoryMode = ('SubCategory', lambda x: x.mode()[0] if not x.mode().empty else np.nan),
    TypeMode = ('type', lambda x: x.mode()[0] if not x.mode().empty else np.nan),
    PurchaseFlag = ('PurchaseFlag', 'first'),
    CampaignFlag = ('CampaignFlag', lambda x: 1 if (x == 1).any() else 0)
).reset_index()

aggregated_df.head()


# In[68]:


# check the missing values
missingness = aggregated_df.isna().sum()
missingness[missingness > 0]


# In[69]:


# fill the missing values with 0 or Unknown for the customers who didn't purchase anything
aggregated_df.fillna({'ItemPriceMean': 0, 'MainCategoryMode': 'Unknown', 'SubCategoryMode': 'Unknown', 'TypeMode': 'Unknown'}, inplace = True)


# In[70]:


# double check the missing values
missingness = aggregated_df.isna().sum()
missingness[missingness > 0]


# In[71]:


aggregated_df.shape


# In[72]:


path2 = '/Users/ilaydabekircan/Documents/Vision_Bridge/DS_Assignment/py_files/df_clean.csv'
aggregated_df.to_csv(path2, index = False)

