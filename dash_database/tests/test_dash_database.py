#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""Additional tests (there are already tests with doctest) for dash_database.DashDatabase class."""

from dash_database import DashDatabase


# # Check if errors are successfully raised

# In[2]:


dash_db = DashDatabase()

# store user value with wrong type for user_id
try:
    dash_db.store_user_value(user_id = ['test'], key_name = 'test', value = 'test')
except TypeError as e:
    print(e)
    
# get user value with wrong type for user_id
try:
    dash_db.get_user_value(user_id = ['test'], key_name = 'test')
except TypeError as e:
    print(e)
    
# get user value with wrong type for key_name
try:
    dash_db.get_user_value(user_id = 'test', key_name = ['test'])
except TypeError as e:
    print(e)
    
# delete value from non existing key with if_not_exists = 'raise'
try:
    dash_db.delete_user_value(user_id = 123, key_name = 'test', if_not_exists = 'raise')
except KeyError as e:
    print(e)
    
# use other value than 'raise' or 'ignore' for if_not_exists
try:
    dash_db.delete_user_value(user_id = 123, key_name = 'test', if_not_exists = 'banana')
except ValueError as e:
    print(e)


# # Other tests not covered by doctest

# In[3]:


# delete non existing key with if_not_exists = 'ignore'
dash_db.delete_user_value(user_id = 123, key_name = 'test', if_not_exists = 'ignore')

# representation of DashDatabase
print(dash_db)

