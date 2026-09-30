from keys import valid_key

for value in ['report', 'A_12', 'x-y']:
    assert valid_key(value), value
for value in ['', '..', '../secret', '/etc/passwd', 'a/b', 'a\\b', 'a.txt', 'bad key', 'é']:
    assert not valid_key(value), value
