# CNRS Scientific Toolkit v0.11.1 patch package

This package contains every file changed or added by patch items 1–7:

- corrected legacy classifier;
- corrected legacy regression tests;
- cross-API consistency tests;
- v0.11.1 release notes;
- v0.11.0 historical warning note;
- v0.11.1 test-status template;
- GitHub release text;
- automated repository patch script.

## Apply to the full v0.11.0 repository

```bash
python apply_v0_11_1_patch.py /path/to/CNRS_Scientific_Toolkit
cd /path/to/CNRS_Scientific_Toolkit
python -m pytest
python -m build
python -m twine check dist/*
```

After the complete test run, replace validation placeholders with the exact results and create the `v0.11.1` tag. Do not alter the existing `v0.11.0` tag.
