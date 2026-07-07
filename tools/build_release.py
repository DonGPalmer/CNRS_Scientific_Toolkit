#!/usr/bin/env python3
"""Create a clean CNRS release tree."""

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]

def clean():
    for p in list(ROOT.rglob('__pycache__')) + list(ROOT.rglob('.pytest_cache')):
        shutil.rmtree(p)
    for p in list(ROOT.rglob('*.pyc')) + list(ROOT.rglob('*.pyo')):
        p.unlink()

def verify():
    bad=[]
    for p in ROOT.rglob('*'):
        if '__pycache__' in str(p) or p.name.endswith(('.pyc','.pyo')):
            bad.append(str(p))
    if bad:
        raise RuntimeError(bad)

if __name__ == '__main__':
    clean()
    verify()
    print('Clean release tree verified')
