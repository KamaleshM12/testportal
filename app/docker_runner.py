import os
import shlex
import docker
import time
from typing import List, Dict, Any


def _read_output(raw: bytes) -> str:
    if raw is None:
        return ""
    if isinstance(raw, tuple):
        out = b"".join([p for p in raw if p])
    else:
        out = raw
    try:
        return out.decode('utf-8', errors='replace')
    except Exception:
        return str(out)


def run_submission(
    workspace_host_path: str,
    image: str,
    compile_cmd: str,
    run_cmd: str,
    input_files: List[str],
    mem_limit: str = '256m',
    cpus: float = 0.5,
    timeout_seconds: int = 5,
) -> Dict[str, Any]:
    client = docker.from_env()
    container = None
    nano_cpus = int(cpus * 1e9)
    try:
        container = client.containers.run(
            image,
            command="/bin/bash",
            detach=True,
            tty=True,
            working_dir='/workspace',
            volumes={workspace_host_path: {'bind': '/workspace', 'mode': 'rw'}},
            network_mode='none',
            read_only=True,
            tmpfs={'/tmp': ''},
            security_opt=['no-new-privileges'],
            cap_drop=['ALL'],
            mem_limit=mem_limit,
            nano_cpus=nano_cpus,
        )

        # Compile step (if any)
        compile_output = ''
        compile_success = True
        if compile_cmd:
            rc, out = container.exec_run(cmd=['/bin/bash', '-lc', compile_cmd], workdir='/workspace')
            compile_output = _read_output(out)
            compile_success = (rc == 0)

        tests = []
        if compile_success:
            for idx, input_fn in enumerate(input_files):
                input_container_path = f'/workspace/{os.path.basename(input_fn)}'
                # build an isolated run that records time and memory using GNU time
                safe_run = run_cmd
                cmd = (
                    "/bin/bash -lc "
                    + shlex.quote(
                        f"/usr/bin/time -f 'TIME:%e\nMEM:%M' timeout {timeout_seconds}s sh -c '{safe_run} < {input_container_path}' 1>prog_out.txt 2>prog_time.txt; echo '---PROG---'; cat prog_out.txt; echo '---TIME---'; cat prog_time.txt"
                    )
                )
                rc, out = container.exec_run(cmd=cmd, workdir='/workspace')
                text = _read_output(out)
                # Split sections
                stdout = ''
                time_str = ''
                mem_str = ''
                if '---PROG---' in text:
                    parts = text.split('---PROG---')[-1]
                    if '---TIME---' in parts:
                        prog_out, time_part = parts.split('---TIME---', 1)
                        stdout = prog_out.strip()
                        time_lines = time_part.strip().splitlines()
                        for line in time_lines:
                            if line.startswith('TIME:'):
                                time_str = line.split('TIME:')[1].strip()
                            if line.startswith('MEM:'):
                                mem_str = line.split('MEM:')[1].strip()
                else:
                    stdout = text.strip()

                # Read expected output from helper (executor will pass expected)
                tests.append({
                    'stdout': stdout,
                    'time_seconds': float(time_str) if time_str else None,
                    'memory_kb': int(mem_str) if mem_str else None,
                    'exit_code': rc,
                })

        return {
            'compile_success': compile_success,
            'compile_output': compile_output,
            'tests': tests,
        }

    finally:
        try:
            if container:
                container.remove(force=True)
        except Exception:
            pass
