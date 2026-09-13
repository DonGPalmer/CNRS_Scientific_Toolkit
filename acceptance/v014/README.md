# v0.14.0 preimplementation acceptance suite

This suite froze the public contract before implementation. Its recorded
preimplementation state was RED because cnrs.streaming_division and
cnrs.witnesses did not yet exist. The implementation candidate is now GREEN.

During implementation run:

~~~bash
python -m pytest -q acceptance/v014
~~~

Do not weaken or delete an acceptance assertion merely to obtain GREEN. If the contract must change, amend the freeze record through governed change control first.
