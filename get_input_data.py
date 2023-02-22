import os
import emission.core.wrapper.user as ecwu
import emission.core.get_database as edb
import pandas as pd


if __name__ == "__main__":
    query = {
            '$and': [
                {'metadata.key': 'analysis/confirmed_trip'},
                {'data.start_ts': {'$exists': True}},
            ]
        }

    tokens_file = os.getcwd() + '/data/tokens.csv'
    try:
        with open(tokens_file) as f:
            tokens = list()
            for token in f:
                tokens.append(token.strip())
            uuids = [ecwu.User.fromEmail(token).uuid for token in tokens]
            query['$and'].append({'user_id': {'$in': uuids}})
    except Exception as e:
        print(e)

    projection = {
        '_id': 0,
        'user_id': 1,
        'trip_start_time_str': '$data.start_fmt_time',
        'trip_end_time_str': '$data.end_fmt_time',
        'timezone': '$data.start_local_dt.timezone',
        'start_coordinates': '$data.start_loc.coordinates',
        'end_coordinates': '$data.end_loc.coordinates',
        'travel_modes': '$data.user_input.trip_user_input.data.jsonDocResponse.data.travel_mode',
        'user_input': '$data.user_input',
    }

    query_result = edb.get_analysis_timeseries_db().find(query, projection)
    print(query_result)
    df = pd.json_normalize(list(query_result))
    if not df.empty:
        df['user_id'] = df['user_id'].apply(lambda x: str(x.as_uuid(3)))

    df.to_csv(os.getcwd() + '/data/res.csv', index=True, encoding='utf-8')  # False: not include index
