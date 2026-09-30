from client import parse_response
from endpoint import display_user

assert parse_response({'data': {'display_name': 'Ada'}}) == 'Ada'
assert display_user({'data': {'display_name': 'Ada'}}) == 'Ada'
assert display_user({'data': {'display_name': ''}}) == 'Anonymous'
try:
    parse_response({'error': 'unavailable'})
except ValueError:
    pass
else:
    raise AssertionError('server errors must not masquerade as users')
