from client import parse_response


def display_user(response):
    return parse_response(response).upper()
