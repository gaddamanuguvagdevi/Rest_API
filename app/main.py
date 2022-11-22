from flask import Flask, request
import json
import pickle
from datetime import datetime

app = Flask(__name__)


@app.route('/temp', methods=['POST'])
def post_temperature():
    data = request.get_json()
    if 'data' in data:
        if isDataValid(data['data']):
            status = 200
            response_data = get_valid_response(data)
        else:
            update_errors(data)
            response_data = {"error": "bad request"}
            status = 400
    else:
        response_data = {"field_missing": "data field missing"}
        status = 400
    response = app.response_class(
        response=json.dumps(response_data),
        status=status,
        mimetype='application/json'
    )
    return response


def update_errors(data):
    errors = read_errors()
    if 'errors' in errors:
        errors['errors'].append(data['data'])
    else:
        errors['errors'] = [data['data']]
    save_errors(errors)


def get_valid_response(data):
    parsed_data = data['data'].split(":")
    temperature = float(parsed_data[3])
    if temperature >= 90:
        response_data = {"overtemp": True, "device_id": parsed_data[0],
                         "formatted_time": datetime.now().strftime("%Y/%m/%d %H:%M:%S")}
    else:
        response_data = {"overtemp": False}
    return response_data


@app.route('/errors', methods=['GET'])
def get_errors():
    errors = read_errors()
    if "errors" not in errors:
        errors['errors'] = []
    return app.response_class(
        response=json.dumps(errors),
        status=200,
        mimetype='application/json'
    )


@app.route('/errors', methods=['DELETE'])
def delete_errors():
    save_errors({})
    return app.response_class(
        response=json.dumps({"success": "error buffered cleared"}),
        status=200,
        mimetype='application/json'
    )


def isfloat64(num):
    try:
        return True if -1.7976931348623157e+308 <= float(num) <= 1.7976931348623157e+308 else False
    except ValueError:
        return False


def isint32(num):
    try:
        return True if (-2 ** 31) <= int(num) <= ((2 ** 31) - 1) else False
    except ValueError:
        return False


def isint64(num):
    try:
        return True if (-2 ** 63) <= int(num) <= ((2 ** 63) - 1) else False
    except ValueError:
        return False


def isDataValid(data):
    data_parameters = data.split(":")
    if len(data_parameters) == 4 and isint32(data_parameters[0]) and isint64(data_parameters[1]) and data_parameters[
        2] == \
            "'Temperature'" and isfloat64(data_parameters[3]):
        return True
    else:
        return False


def save_errors(dictionary):
    with open('saved_errors.pkl', 'wb') as f:
        pickle.dump(dictionary, f)


def read_errors():
    try:
        with open('saved_errors.pkl', 'rb') as f:
            loaded_dict = pickle.load(f)
    except EOFError:
        loaded_dict = {'errors': []}
    return loaded_dict
