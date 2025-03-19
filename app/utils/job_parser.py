import re

def parse_squeue_output(output):
    lines = output.strip().split("\n")
    if len(lines) < 2:
        return []
    header = re.split(r'\s+', lines[0].strip())
    jobs = []
    for line in lines[1:]:
        row = re.split(r'\s+', line.strip(), maxsplit=len(header) - 1)
        if len(row) == len(header):
            job_entry = dict(zip(header, row))
            jobs.append(job_entry)
    return jobs
