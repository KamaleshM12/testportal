import os
import tempfile
import uuid
import shutil
from typing import List
from .docker_runner import run_submission
from .schemas import TestCase


DEFAULT_RUNNER_IMAGE = os.getenv('RUNNER_IMAGE', 'testportal/runner:latest')

LANG_CONFIG = {
    'python': {
        'image': DEFAULT_RUNNER_IMAGE,
        'compile': '',
        'run': 'python3 main.py',
        'source_name': 'main.py',
    },
    'java': {
        'image': DEFAULT_RUNNER_IMAGE,
        'compile': 'javac Main.java',
        'run': 'java Main',
        'source_name': 'Main.java',
    },
    'cpp': {
        'image': DEFAULT_RUNNER_IMAGE,
        'compile': 'g++ -O2 -std=gnu++17 main.cpp -o main.out',
        'run': './main.out',
        'source_name': 'main.cpp',
    },
}


def execute(code: str, language: str, tests: List[TestCase]):
    lang = language.lower()
    if lang not in LANG_CONFIG:
        raise ValueError('unsupported language')

    cfg = LANG_CONFIG[lang]
    workdir = tempfile.mkdtemp(prefix='exec_')
    try:
        src_path = os.path.join(workdir, cfg['source_name'])
        with open(src_path, 'w', encoding='utf-8') as f:
            f.write(code)

        # write inputs
        input_files = []
        for i, t in enumerate(tests):
            fn = os.path.join(workdir, f'input_{i}.txt')
            with open(fn, 'w', encoding='utf-8') as fh:
                fh.write(t.input)
            input_files.append(fn)

        # Run in Docker
        result = run_submission(
            workspace_host_path=workdir,
            image=cfg['image'],
            compile_cmd=cfg['compile'],
            run_cmd=cfg['run'],
            input_files=input_files,
            mem_limit='256m',
            cpus=0.5,
            timeout_seconds=5,
        )

        # Post-process into test results
        tests_out = []
        for idx, raw in enumerate(result.get('tests', [])):
            expected = tests[idx].expected_output.strip()
            stdout = raw.get('stdout', '').strip()
            passed = (stdout == expected)
            tests_out.append({
                'stdout': stdout,
                'stderr': None,
                'time_seconds': raw.get('time_seconds'),
                'memory_kb': raw.get('memory_kb'),
                'passed': passed,
            })

        return {
            'compile_success': result.get('compile_success', True),
            'compile_output': result.get('compile_output', ''),
            'tests': tests_out,
        }

    finally:
        try:
            shutil.rmtree(workdir)
        except Exception:
            pass
