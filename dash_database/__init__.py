#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""Initializes the dash_database library.

Imports the DashDatabase class which is the main object of the dash_database library.
"""

import sqlitedict
import re


# # DashDatabase

# In[2]:


class DashDatabase():
    """The DashDatabase class manages the values of the users of a dash app.
    It creates a sqlitedict database (sqlitedict.SqliteDict) in autocommit mode which works more or 
    less like a python dictionnary (sqlitedict_db['key'] = value) but the values are stored within a sqlite file. 
    It is thread safe so you can use it in Dash like you would use redis for instance. 
    
    More information on the sqlitedict GitHub repository.
    
    In each method of DashDatabase there is an argument "user_id". 
    With DashDatabase you can use the same key names for all users and DashDatabase will internally prepend the user_id
    internally so that user A and user B have their own data under the same key.
    Under the hood the full key names look like this:
        123_password (user_id 123, key name password)
        456_password (user_id 456, key name password)
        
    The user id can be anything you want (it can be for instance a session id as well) but you need to make sure
    that the data is assigned to the correct user! You should definitely see "Example integration within dash app" 
    to handle this.
    
    Args:
        db_location: filepath where the database will be stored. 
            By default None which stores the database in a temporary file path and deletes it after the class instance expires.
    
    Usage:
        >>> from dash_database import DashDatabase

        >>> # create an instance of DashDatabase
        >>> dash_db = DashDatabase(db_location = None)
        
        >>> # save values for user 123
        >>> dash_db.store_user_value(user_id = 123, key_name = 'account_id', value = 46887)
        >>> dash_db.store_user_value(user_id = 123, key_name = 'favorite_animal', value = 'yellow')
        >>> dash_db.list_stored_user_keys(123) # list the names of the keys use by the user

        >>> # save values for user 456
        >>> dash_db.store_user_value(user_id = 456, key_name = 'account_id', value = 87874)
        >>> dash_db.store_user_value(456, 'favorite_color', 'green')
        >>> dash_db.list_stored_user_keys(456) # list the names of the keys use by the user

        >>> # get the value behind a user key
        >>> dash_db.get_user_value(user_id = 123, key_name = 'favorite_animal')

        >>> # delete a key and its value for a user
        >>> dash_db.delete_user_value(user_id = 123, key_name = 'favorite_animal', 
        ...                           if_not_exists = 'ignore') # if 'raise' raises an Error when a key is not found (default 'ignore')

        >>> # delete all keys and their values for a user
        >>> dash_db.delete_all_user_values(456)

        >>> # list all keys of the users again for testing purposes
        >>> dash_db.list_stored_user_keys(123)
        >>> dash_db.list_stored_user_keys(456)
        

    Example integration within dash app:
    
        See ./dash_database/README.MD
    
    """
    
    
    
    def __init__(self, db_location = None):
        """Creates an instance of the DashDatabase class."""
        
        self.db = sqlitedict.SqliteDict(filename = db_location, autocommit = True)        

        def _create_unique_key_name(user_id, key_name):
            """Creates a unique key name in sqlitedict by using the user id (see class docstring)."""
            unique_key_name = f'{user_id}_{key_name}'
            return unique_key_name
        
            
        self._create_unique_key_name = _create_unique_key_name


    def list_stored_user_keys(self, user_id):
        """See class docstring for usage"""
        # get list of keys starting with user_id
        user_keys = [key for key in self.db.keys() if key.startswith(str(user_id))]
        
        # remove user_id from the key names
        user_keys = [re.sub(f'{re.escape(str(user_id))}\_','',str(key)) for key in user_keys]
        return user_keys
    
    def store_user_value(self, user_id, key_name, value):
        """See class docstring for usage"""
        unique_key_name = self._create_unique_key_name(user_id, key_name)
        self.db[unique_key_name] = value

    def get_user_value(self, user_id, key_name):
        """See class docstring for usage"""
        unique_key_name = self._create_unique_key_name(user_id, key_name)
        return self.db.get(unique_key_name)


    def delete_user_value(self, user_id, key_name, if_not_exists = 'ignore'):
        """See class docstring for usage"""
        unique_key_name = self._create_unique_key_name(user_id, key_name)
        
        if if_not_exists == 'ignore':
            
            try:
                self.db.pop(unique_key_name)
            except KeyError:
                pass
            
        elif if_not_exists == 'raise':
            self.db.pop(unique_key_name)
            
        else:
            raise ValueError('if_not_exists must be either "ignore" or "raise"')
            
            
    def delete_all_user_values(self, user_id):
        """See class docstring for usage"""
        
        user_keys = self.list_stored_user_keys(user_id = user_id)
        
        for key in user_keys:
            self.delete_user_value(user_id = user_id, key_name = key)
        

    def __repr__(self):
        repr_str = []
        repr_str.append(f'DashDatabase at {self.db.filename}')

        # assemble string
        repr_str = ''.join(repr_str)
        
        return repr_str

