[![CircleCI](https://circleci.com/gh/ThibTrip/dash_database.svg?style=svg)](https://circleci.com/gh/ThibTrip/dash_database) [![codecov](https://codecov.io/gh/ThibTrip/dash_database/branch/master/graph/badge.svg)](https://codecov.io/gh/ThibTrip/dash_database)

# dash_database

Manages user values for a [dash](https://github.com/plotly/dash) app. This is an alternative solution for [sharing data between callbacks](https://dash.plot.ly/sharing-data-between-callbacks) based on the library sqlitedict. 

It has the following benefits:

* easy installation via git clone and pip install (I would like to push dash_database to PyPI to make it even easier but want to make sure there aren't any issues inherent to using sqlitedict first) unlike redis
* no need to fiddle with json dumps and pickles unlike redis or dcc.Store. It takes any picklable objects out of the box.
* no need to have a redis server running
* it is thread safe
* it can work in memory

# Installation

```
pip install dash-database
```

# Usage

## Basic usage

Import the main object DashDatabase and you can start managing data already. Detailled information on the arguments of DashDatabase's methods and how the class was implemented can be found in its docstring.

```python
from dash_database import DashDatabase

# create an instance of DashDatabase
dash_db = DashDatabase(db_location = None) # if None it is created in a temp folder and deleted after use

# save values for user 123
dash_db.store_user_value(user_id = 123, key_name = 'account_id', value = 46887)
dash_db.store_user_value(user_id = 123, key_name = 'favorite_animal', value = 'monkey')
dash_db.list_stored_user_keys(123) # list the names of the keys used by the user
['account_id', 'favorite_animal']

# save values for user 456
dash_db.store_user_value(user_id = 456, key_name = 'account_id', value = 87874)
dash_db.store_user_value(456, 'favorite_color', 'green')
dash_db.list_stored_user_keys(456) # list the names of the keys used by the user
['account_id', 'favorite_color']

# get the value behind a user key
dash_db.get_user_value(user_id = 123, key_name = 'favorite_animal')
'monkey'

# delete a key and its value for a user
dash_db.delete_user_value(user_id = 123, key_name = 'favorite_animal', 
                          # when if_not_exists is equal to "raise" you get an error if a key does not exist
                          # if it is equal to "ignore" nothing happens if it does not exist (default)
                          if_not_exists = 'ignore') 

# delete all keys and their values for a user
dash_db.delete_all_user_values(456)

# list all keys of the users again for testing purposes
dash_db.list_stored_user_keys(123)
['account_id']
dash_db.list_stored_user_keys(456)
[]
```

## Example with a dash app

```python
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_database import DashDatabase
import uuid

def serve_layout():
    """Creates the layout for each user of the app.
    This function is executed each time a session is created for the app.
    It creates a new session id (a uuid.uuid1 as string) each time.

    This session id will be used in combination with a DashDatabase instance to manage user values.
    It will be fetched via the property data of a dcc.Store component.
    """
    
    # create a session id
    session_id = str(uuid.uuid1())
    
    # store the session id in a dcc.Store component (invisible component for storing data)
    store_session_id_div = dcc.Store(id='session_id_div_id', 
                                     storage_type = 'session', # IMPORTANT! see docstring of dcc.Store 
                                     data = session_id)
    
    # create tab to enter a value
    first_tab = dcc.Tab(label = "Enter a value", 
                        children = [dcc.Input(placeholder = "Enter value here", id = "input_div"),
                                    html.Button(children = "OK", id = "ok_button"),
                                    dcc.Markdown(id = "success_value_saved")])
    
    # create tab to retrieve the value entered in the other tab
    second_tab = dcc.Tab(label = "Retrieve the value",
                         children = [html.Button(children = "Show me the value", id = "show_value_button"),
                                     dcc.Markdown(id = "show_value_div")])
    
    # assemble tabs in dcc.Tabs object
    tabs = dcc.Tabs(children = [first_tab, second_tab])

    
    # create layout
    layout = html.Div(children = [tabs, store_session_id_div])

    
    return layout


# putting your callbacks in functions is a nice trick to be able to move them in other modules and import them 
def create_callback_save_value(app:dash.Dash, 
                               dash_db:DashDatabase):
    @app.callback(Output('success_value_saved', 'children'),
                  [Input('ok_button', 'n_clicks')], # the button triggers the callback
                  [State('input_div', 'value'), # additional info that does not trigger the callback 
                   State('session_id_div_id', 'data')]) # used to identify the user and save its data
    def save_value(n_clicks, value, session_id):
        
        # when the app starts all callbacks are triggered by default. 
        # raise a PreventUpdate to avoid the callback trigger at start (n_clicks is None at this point)
        if n_clicks is None:
            raise PreventUpdate
            
        # save value 
        dash_db.store_user_value(user_id = session_id, 
                                 key_name = 'value', 
                                 value = value)
        
        # return success message
        return "Your value was sucessfully saved. Try to retrieve it in the other tab now :)!"
    
def create_callback_retrieve_value(app:dash.Dash, 
                                   dash_db:DashDatabase):
    @app.callback(Output('show_value_div', 'children'),
                  [Input('show_value_button', 'n_clicks')],
                  [State('session_id_div_id', 'data')])
    def retrieve_value(n_clicks, session_id):
        
        # when the app starts all callbacks are triggered by default. 
        # raise a PreventUpdate to avoid the callback trigger at start (n_clicks is 0 at this point)
        if n_clicks is None:
            raise PreventUpdate
            
        # save value 
        value = dash_db.get_user_value(user_id = session_id, 
                                       key_name = 'value')
        
        # return success message
        return f"Your value is {value}"
    
    
# create the app, add the layout and the callbacks
app = dash.Dash()
app.layout = serve_layout
dash_db = DashDatabase() # create a DashDatabase instance for managing user values
create_callback_save_value(app, dash_db)
create_callback_retrieve_value(app, dash_db)

if __name__ == "__main__":
    app.run_server(debug = True) # set to False if running in a Jupyter Notebook or in Jupyter Lab!
    
```
