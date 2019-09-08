#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""Additional tests (there are already tests with doctest) for dash_database.DashDatabase class."""

from dash_database import DashDatabase


# # Check if errors are successfully raised

# In[2]:


dash_db = DashDatabase()

try:
    dash_db.store_user_value(user_id = ['test'], key_name = 'test', value = 'test')
except TypeError as e:
    print(e)
    
try:
    dash_db.get_user_value(user_id = ['test'], key_name = 'test')
except TypeError as e:
    print(e)
    
try:
    dash_db.get_user_value(user_id = 'test', key_name = ['test'])
except TypeError as e:
    print(e)
    
try:
    dash_db.delete_user_value(user_id = 123, key_name = 'test', if_not_exists = 'raise')
except KeyError as e:
    print(e)

