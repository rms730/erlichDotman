import doctest
from pathlib import Path

text = Path('README.md').read_text()
assert 'clamp(-2)' in text and 'clamp(20)' in text
assert doctest.testfile('README.md', module_relative=False).failed == 0
