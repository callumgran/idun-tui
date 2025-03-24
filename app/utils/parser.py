import re

sacct_states = [
    'BOOT_FAIL',
    'CANCELLED',
    'COMPLETED',
    'DEADLINE',
    'FAILED',
    'NODE_FAIL',
    'OUT_OF_MEMORY',
    'PENDING',
    'PREEMPTED',
    'RUNNING',
    'SUSPENDED',
    'TIMEOUT'
]

def parse_squeue_output(output: str, username: str) -> list:
    """Parse raw sacct output into structured data."""
    lines = output.strip().split("\n")
    if len(lines) < 2:
        return []
    header = re.split(r'\s+', lines[0].strip())
    jobs = []
    for line in lines[1:]:
        row = re.split(r'\s+', line.strip())

        job_name = ""
        i = 2
        while (row[i] != username):
            job_name += row[i] + " "
            i += 1

        output_row = row[:2] + [job_name.strip()[:30]] + row[i:]

        print(row)
        print(output_row)
        print(len(output_row))
        print(len(header))
        
        if len(output_row) == len(header):
            job_entry = dict(zip(header, output_row))
            jobs.append(job_entry)
    return jobs

def parse_sacct_output(output: str) -> list:
    """Parse raw sacct output into structured data."""
    lines = output.strip().split("\n")
    if len(lines) < 2:
        return []
    header = re.split(r'\s+', lines[0].strip())
    jobs = []
    for line in lines[1:]:
        if set(line.strip()) <= {'-', ' '}:
            continue

        print(line)
        row = re.split(r'\s+', line.strip())

        job_name = ""
        i = 1
        while i < len(row) and not any(state in row[i] for state in sacct_states):
            job_name += row[i] + " "
            i += 1

        output_row = row[:1] + [job_name.strip()[:30]] + row[i:]

        print(output_row)
        print(len(output_row))
        print(len(header))
        
        if len(output_row) == len(header):
            job_entry = dict(zip(header, output_row))
            jobs.append(job_entry)
    return jobs

def parse_vncserver_output(output: str) -> list:
    """Parse raw sacct output into structured data."""
    lines = output.strip().split("\n")[2:]
    if len(lines) < 2:
        return []
    header = re.split(r'\t', lines[0].strip())

    servers = []
    for line in lines[1:]:
        if set(line.strip()) <= {'-', ' '}:
            continue

        row = re.split(r'\t\t', line.strip())

        if len(row) == len(header):
            vnc_entry = dict(zip(header, row))
            servers.append(vnc_entry)
    return servers