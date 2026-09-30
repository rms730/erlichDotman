from dedupe import deduplicate


class Key:
    comparisons = 0
    def __init__(self, value):
        self.value = value
    def __hash__(self):
        return hash(self.value)
    def __eq__(self, other):
        Key.comparisons += 1
        return self.value == other.value
items = [Key(i) for i in range(500)]
assert deduplicate(items) == items
assert Key.comparisons < 2000, 'deduplication regressed to quadratic comparisons'
assert deduplicate(['b', 'a', 'b', 'c']) == ['b', 'a', 'c']
