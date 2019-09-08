#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""Initializes the dash_database library.

Imports the DashDatabase class which is the main object of the dash_database library.
"""

import sqlitedict
import re
import typing

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
        
    The user id can be anything you want  as long as it is a str or an int (it can be for instance a session id as well) but 
    you need to make sure that the data is assigned to the correct user of your dash app! You should definitely see 
    "Example integration within dash app" (below Usage in this docstring) to handle this.
    
    Args:
        db_location: ':memory:', None or a filepath
            if ':memory:' (default) the database exists in memory until the class instance expires 
                This offers the best performance (see ./dash_database/tests/performance_tests.ipynb)
            if None the database exists in a temporary file path and gets deleted after the class instance expires
            if a filepath the database exists in given filepath and stays after the class instance expires
    
    Usage:
        >>> from dash_database import DashDatabase

        >>> # create an instance of DashDatabase
        >>> dash_db = DashDatabase(db_location = None) # if None it is created in a temp folder and deleted after use

        >>> # save values for user 123
        >>> dash_db.store_user_value(user_id = 123, key_name = 'account_id', value = 46887)
        >>> dash_db.store_user_value(user_id = 123, key_name = 'favorite_animal', value = 'monkey')
        >>> dash_db.list_stored_user_keys(123) # list the names of the keys used by the user
        ['account_id', 'favorite_animal']

        >>> # save values for user 456
        >>> dash_db.store_user_value(user_id = 456, key_name = 'account_id', value = 87874)
        >>> dash_db.store_user_value(456, 'favorite_color', 'green')
        >>> dash_db.list_stored_user_keys(456) # list the names of the keys used by the user
        ['account_id', 'favorite_color']

        >>> # get the value behind a user key
        >>> dash_db.get_user_value(user_id = 123, key_name = 'favorite_animal')
        'monkey'

        >>> # delete a key and its value for a user
        >>> dash_db.delete_user_value(user_id = 123, key_name = 'favorite_animal', 
        ...                           # when if_not_exists is equal to "raise" you get an error if a key does not exist
        ...                           # if it is equal to "ignore" nothing happens if it does not exist (default)
        ...                           if_not_exists = 'ignore') 

        >>> # delete all keys and their values for a user
        >>> dash_db.delete_all_user_values(456)

        >>> # list all keys of the users again for testing purposes
        >>> dash_db.list_stored_user_keys(123)
        ['account_id']
        >>> dash_db.list_stored_user_keys(456)
        []
        

    Example integration within dash app:
    
        See ./dash_database/README.MD
    
    """
    
    
    
    def __init__(self, db_location = ':memory:'):
        """Creates an instance of the DashDatabase class."""
        
        self.db = sqlitedict.SqliteDict(filename = db_location, autocommit = True)        

        def _create_unique_key_name(user_id, key_name):
            """Creates a unique key name in sqlitedict by using the user id (see class docstring).
            
            Args:
                user_id: unique identifier (str or int)
                key_name: non unique identifier (str or int, gets attached to the user_id internaly)
                
            Usage:
               >>> _create_unique_key_name(user_id = 123, key_name = 'password')
               '123_password'
            
            """
            unique_key_name = f'{user_id}_{key_name}'
            return unique_key_name
        
        def _verify_types(user_id, key_name = None):
                        
            # user_id is always used an argument so we can always test it
            tested_types_user_id = tuple([str,int])
                        
            if not isinstance(user_id,tested_types_user_id):
                raise TypeError(f'the type user_id can only be one of {tested_types_user_id} (for stability reasons as other types were not tested)')
            
            # key_name is not always used so check if it is not None first
            tested_types_key_name = tuple([str,int])

            if key_name is not None:
                if not isinstance(key_name,tested_types_key_name):
                    raise TypeError(f'the type key_name can only be one of {tested_types_key_name} (for stability reasons as other types were not tested)')
        
        self._create_unique_key_name = _create_unique_key_name
        self._verify_types = _verify_types
        


    def list_stored_user_keys(self, user_id):
        """Lists all keys in use from given user_id.
        
        Args:
            user_id: unique identifier (str or int)
        
        Usage:
            see docsting of DashDatabase
        
        """
        self._verify_types(user_id)
        
        # get list of keys starting with user_id
        user_keys = [key for key in self.db.keys() if key.startswith(str(user_id))]
        
        # remove user_id from the key names
        user_keys = [re.sub(f'{re.escape(str(user_id))}\_','',str(key)) for key in user_keys]
        return user_keys
    
    def store_user_value(self, user_id, key_name, value):
        """Store a value for given user id with given key name.
        
        Args:
            user_id: unique identifier (str or int)
            key_name: non unique identifier (str or int, gets attached to the user_id internally)
            value: can be any picklable object.

        Usage:
            see docsting of DashDatabase
        """
        self._verify_types(user_id, key_name)

        unique_key_name = self._create_unique_key_name(user_id, key_name)
        self.db[unique_key_name] = value

    def get_user_value(self, user_id, key_name):
        """Gets a value for given user id from given key name.
        Returns None if the key does not exist for given user id.
        
        Args:
            user_id: unique identifier (str or int)
            key_name: non unique identifier (str or int, attached to the user_id)

        Usage:
            see docsting of DashDatabase
        """       
        self._verify_types(user_id, key_name)
        
        unique_key_name = self._create_unique_key_name(user_id, key_name)
        return self.db.get(unique_key_name)


    def delete_user_value(self, user_id, key_name, if_not_exists = 'ignore'):
        """Deletes a value and the corresponding key for given user id.
        
        Args:
            user_id: unique identifier (str or int)
            key_name: non unique identifier (str or int, attached to the user_id)
            if_not_exists: only relevant if the key does not exist, in this case:
                if 'ignore' (default) nothing happens
                if 'raise' raises a KeyError

        Usage:
            see docsting of DashDatabase
        """   
        self._verify_types(user_id, key_name)
        
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
        """Deletes all values and their corresponding keys for given user id.
        
        Args:
            user_id: unique identifier (str or int)

        Usage:
            see docsting of DashDatabase
        """
        self._verify_types(user_id)
        
        user_keys = self.list_stored_user_keys(user_id = user_id)
        
        for key in user_keys:
            self.delete_user_value(user_id = user_id, key_name = key)
        

    def __repr__(self):
        """Create representation for DashDabase (show location of database)."""
        repr_str = f'DashDatabase at "{self.db.filename}"'
        return repr_str
    
if __name__ == "__main__":
    import doctest
    doctest.testmod(raise_on_error = True, verbose = True)