import json
from pathlib import Path
import subprocess
import sys
import tempfile


def run():
    root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(dir=root) as temporary:
        converted = Path(temporary) / 'converted.json'
        report = Path(temporary) / 'report.json'
        subprocess.run([sys.executable, str(root / 'transform.py'),
                        str(root / 'orders.json'), str(converted)], check=True)
        rows = json.loads(converted.read_text(encoding='utf-8'))
        assert rows == [{'id': 'b', 'net_cents': 3000},
                        {'id': 'a', 'net_cents': 2000},
                        {'id': 'c', 'net_cents': 0}], rows
        subprocess.run([sys.executable, str(root / 'report.py'),
                        str(converted), str(report)], check=True)
        actual = json.loads(report.read_text(encoding='utf-8'))
        assert actual == {'count': 3, 'total_cents': 5000,
                          'ids': ['a', 'b', 'c']}, actual
    print('PASS: conversion and report outputs')


if __name__ == '__main__':
    run()
