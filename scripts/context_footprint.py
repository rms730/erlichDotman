"""Report approximate instruction overhead; never tokenize or transmit private context."""

import argparse
import json
import math
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = 'AGENTS.md'
SKILL = 'skills/engineering-cascade/SKILL.md'
EXAMPLE_INPUTS = ('examples/project.json', 'examples/task.json')


def _git(*arguments):
    executable = shutil.which('git')
    if executable is None:
        raise OSError('git is unavailable')
    return subprocess.check_output(  # noqa: S603 - fixed Git commands, without a shell.
        [executable, *arguments], cwd=ROOT, text=True, stderr=subprocess.DEVNULL,
    )


def _snapshot(revision=None):
    if revision:
        revision = _git('rev-parse', '--verify', '--end-of-options',
                        f'{revision}^{{commit}}').strip()
        paths = _git('ls-tree', '-r', '--name-only', revision).splitlines()
    else:
        paths = _git('ls-files', '--cached', '--others', '--exclude-standard').splitlines()
    paths = sorted(set(paths))
    measured = {}
    for filename in paths:
        if (filename not in {AGENTS, SKILL, *EXAMPLE_INPUTS}
                and not filename.startswith(('docs/', 'skills/engineering-cascade/references/'))):
            continue
        if not filename.endswith(('.md', '.json')):
            continue
        if revision is None and not (ROOT / filename).is_file():
            continue  # Deleted tracked references still appear in git ls-files.
        text = (_git('cat-file', 'blob', f'{revision}:{filename}') if revision
                else (ROOT / filename).read_text(encoding='utf-8'))
        measured[filename] = {'characters': len(text), 'words': len(text.split()),
                              'approx_tokens': math.ceil(len(text) / 4)}
    overhead = {name: measured[path]['approx_tokens'] for name, path in (
        ('core_development', AGENTS), ('runtime_orchestration', SKILL),
    )}
    overhead['orchestration_in_core_checkout'] = sum(overhead.values())
    example_inputs = sum(measured[path]['approx_tokens'] for path in EXAMPLE_INPUTS)
    optional = {
        'all_docs': sum(value['approx_tokens'] for path, value in measured.items()
                        if path.startswith('docs/')),
        'all_runtime_references': sum(value['approx_tokens'] for path, value in measured.items()
                                      if '/references/' in path),
    }
    warnings = []
    if measured[SKILL]['approx_tokens'] > 1500:
        warnings.append('Core skill exceeds the 1500-token review target; justify with quality evals.')
    return {'instruction_files': {path: measured[path] for path in (AGENTS, SKILL)},
            'default_instruction_overhead': overhead,
            'normal_orchestration_example': {
                'input_files': list(EXAMPLE_INPUTS), 'input_approx_tokens': example_inputs,
                'skill_plus_inputs_approx_tokens': overhead['runtime_orchestration'] + example_inputs,
            },
            'optional_material_not_loaded_by_default': optional, 'warnings': warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', help='Compare a local commit/ref to the working tree')
    args = parser.parse_args()
    try:
        report = {'method': 'ceil(Unicode characters / 4), including Markdown/frontmatter',
                  'scope': 'Repository-controlled context only; not tokenizer counts or metered usage.',
                  'excludes': ['host/system prompts', 'tool catalogs', 'target-project rules',
                               'actual task source/tests', 'conditionally loaded references'],
                  'after': _snapshot()}
        if args.baseline:
            report['baseline_ref'] = args.baseline
            report['before'] = _snapshot(args.baseline)
        print(json.dumps(report, indent=2))
    except (OSError, subprocess.CalledProcessError, KeyError) as exc:
        raise SystemExit('Unable to measure the requested local snapshot') from exc


if __name__ == '__main__':
    main()
