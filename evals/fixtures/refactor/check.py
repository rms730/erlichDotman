from labels import normalize_labels

assert normalize_labels([' a ', '', 'b', ' a ', '  ']) == ['a', 'b', 'a']
assert normalize_labels([]) == []
assert normalize_labels(['B', 'a', 'B']) == ['B', 'a', 'B']
assert normalize_labels(iter([' a ', ' b '])) == ['a', 'b']
