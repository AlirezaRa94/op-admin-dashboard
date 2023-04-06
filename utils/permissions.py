import json
import os

import requests

from utils.constants import valid_trip_columns, valid_uuids_columns


STUDY_NAME = os.getenv('STUDY_NAME')
PATH = os.getenv('CONFIG_PATH')
CONFIG_URL = PATH + STUDY_NAME + ".nrel-op.json"
response = requests.get(CONFIG_URL)
permissions = json.loads(response.text).get("admin_dashboard", {})


def has_permission(perm):
    return True if permissions.get(perm) is True else False


def get_trips_columns():
    columns = set(valid_trip_columns)
    for column in permissions.get("data_trips_columns_exclude", []):
        columns.discard(column)
    return columns


def get_uuids_columns():
    columns = set(valid_uuids_columns)
    for column in permissions.get("data_uuids_columns_exclude", []):
        columns.discard(column)
    return columns


def get_token_prefix():
    return permissions['token_prefix'] + '_' if permissions.get('token_prefix') else ''


def get_additional_trip_columns():
    additional_columns = permissions.get('additional_trip_columns', [])
    additional_columns.extend([
        {'label': 'trip_start_time_str', 'path': '$data.start_fmt_time'},
        {'label': 'trip_end_time_str', 'path': '$data.end_fmt_time'},
        {'label': 'timezone', 'path': '$data.start_local_dt.timezone'},
        {'label': 'start_coordinates', 'path': '$data.start_loc.coordinates'},
        {'label': 'end_coordinates', 'path': '$data.end_loc.coordinates'},
        {'label': 'travel_mode', 'path': '$data.user_input.trip_user_input.data.jsonDocResponse.data.travel_mode'},
        {'label': 'platform', 'path': '$metadata.platform'},
        {'label': 'user_input_timezone', 'path': '$data.user_input.trip_user_input.metadata.write_local_dt.timezone'},
        {'label': 'label', 'path': '$data.user_input.trip_user_input.data.label'},
        {'label': 'purpose', 'path': '$data.user_input.trip_user_input.data.jsonDocResponse.data.destination_purpose'},
        {'label': 'survey', 'path': '$data.user_input.trip_user_input.data.name'},
        {'label': 'duration', 'path': '$data.duration'},
        {'label': 'distance', 'path': '$data.distance'},
    ])

    return additional_columns
