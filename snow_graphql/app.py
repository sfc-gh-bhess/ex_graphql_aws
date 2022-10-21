import json
import logging
import datetime

import snow_procs
import snow_session

# Set Logging Level
logger = logging.getLogger()
logger.setLevel(logging.INFO)

## HELPERS
date_str = "%Y-%m-%d"
datetime_str = f"{date_str}T%H:%M:%S"
def stringify(doc):
    if (type(doc) == str):
        return doc
    if (type(doc) == dict):
        for k, v in doc.items():
            doc[k] = stringify(v)
    if (type(doc) == list):
        for i in range(len(doc)):
            doc[i] = stringify(doc[i])
    if (type(doc) == datetime.datetime):
        doc = doc.strftime(datetime_str)
    if (type(doc) == datetime.date):
        doc = doc.strftime(date_str)
    return doc
def get_parameter(event, pkey, key):
    return event.get(pkey).get(key) if event.get(pkey) else None

def lambda_handler_busy_airports(event, context):
    logger.info(f"EVENT: {json.dumps(event)}")
    snow_session.get_db_client()
    begin = get_parameter(event, 'arguments', 'begin')
    end = get_parameter(event, 'arguments', 'end')
    deparr = get_parameter(event, 'arguments', 'deparr')
    nrows = get_parameter(event, 'arguments', 'nrows')
    return stringify(snow_procs.busy_airports(snow_session.session, begin, end, deparr, nrows))

def lambda_handler_airport_daily(event, context):
    logger.info(f"EVENT: {json.dumps(event)}")
    snow_session.get_db_client()
    airport = get_parameter(event, 'arguments', 'airport')
    begin = get_parameter(event, 'arguments', 'begin')
    end = get_parameter(event, 'arguments', 'end')
    return stringify(snow_procs.airport_daily(snow_session.session, airport, begin, end))

def lambda_handler_airport_daily_carriers(event, context):
    logger.info(f"EVENT: {json.dumps(event)}")
    snow_session.get_db_client()
    airport = get_parameter(event, 'arguments', 'airport')
    begin = get_parameter(event, 'arguments', 'begin')
    end = get_parameter(event, 'arguments', 'end')
    deparr = get_parameter(event, 'arguments', 'deparr')
    return stringify(snow_procs.airport_daily_carriers(snow_session.session, airport, begin, end, deparr))

