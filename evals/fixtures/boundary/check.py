from numbers import clamp_index

assert clamp_index(-1, 3) == 0
assert clamp_index(0, 3) == 0
assert clamp_index(2, 3) == 2
assert clamp_index(3, 3) == 2
assert clamp_index(20, 3) == 2
try:
    clamp_index(0, 0)
except ValueError:
    pass
else:
    raise AssertionError('empty collection must reject indexing')
