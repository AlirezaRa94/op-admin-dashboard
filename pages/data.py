"""
Note that the callback will trigger even if prevent_initial_call=True. This is because dcc.Location must be in app.py.
Since the dcc.Location component is not in the layout when navigating to this page, it triggers the callback.
The workaround is to check if the input value is None.
"""
from dash import dcc, html, Input, Output, callback, register_page, dash_table

# Etc
import logging
import pandas as pd
from dash.exceptions import PreventUpdate

from utils import permissions as perm_utils
from utils import db_utils

register_page(__name__, path="/data")

intro = """## Data"""

layout = html.Div(
    [   
        dcc.Markdown(intro),
        dcc.Tabs(id="tabs-datatable", value='tab-uuids-datatable', children=[
            # dcc.Tab(label='Demographics survey', value='tab-demographics-survey-datatable'),
            dcc.Tab(label='UUIDs', value='tab-uuids-datatable'),
            dcc.Tab(label='Trips', value='tab-trips-datatable'),
        ]),
        html.Div(id='tabs-content'),
    ]
)


def clean_location_data(df):
    if 'data.start_loc.coordinates' in df.columns:
        df['data.start_loc.coordinates'] = df['data.start_loc.coordinates'].apply(lambda x: f'({x[0]}, {x[1]})')
    if 'data.end_loc.coordinates' in df.columns:
        df['data.end_loc.coordinates'] = df['data.end_loc.coordinates'].apply(lambda x: f'({x[0]}, {x[1]})')
    return df


@callback(
    Output('tabs-content', 'children'),
    Input('tabs-datatable', 'value'),
    Input('store-uuids', 'data'),
    Input('store-trips', 'data'),
)
def render_content(tab, store_uuids, store_trips):
    data, columns, has_perm = None, [], False
    if tab == 'tab-uuids-datatable':
        data = store_uuids["data"]
        logging.debug("Before adding trip data, users data is %s" % data)
        data = db_utils.add_user_stats(data, store_trips["data"])
        logging.debug("After adding trip data, users data is %s" % data)
        columns = perm_utils.get_uuids_columns()
        has_perm = perm_utils.has_permission('data_uuids')
    elif tab == 'tab-trips-datatable':
        data = store_trips["data"]
        columns = perm_utils.get_allowed_trip_columns()
        columns.update(
            col['label'] for col in perm_utils.get_allowed_named_trip_columns()
        )
        has_perm = perm_utils.has_permission('data_trips')
    df = pd.DataFrame(data)
    if df.empty or not has_perm:
        return None

    df = df.drop(columns=[col for col in df.columns if col not in columns])
    df = clean_location_data(df)

    return populate_datatable(df)


def populate_datatable(df):
    if not isinstance(df, pd.DataFrame):
        raise PreventUpdate
    return dash_table.DataTable(
        # id='my-table',
        # columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        export_format="csv",
        filter_options={"case": "sensitive"},
        # filter_action="native",
        sort_action="native",  # give user capability to sort columns
        sort_mode="single",  # sort across 'multi' or 'single' columns
        page_current=0,  # page number that user is on
        page_size=50,  # number of rows visible per page
        style_cell={
            'textAlign': 'left',
            # 'minWidth': '100px',
            # 'width': '100px',
            # 'maxWidth': '100px',
        },
        style_table={'overflowX': 'auto'}
    )
