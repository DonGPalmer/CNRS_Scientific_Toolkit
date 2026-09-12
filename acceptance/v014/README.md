# v0.14.0 preimplementation acceptance suite

This suite freezes the public contract before implementation. At freeze time it must fail during collection because cnrs.streaming_division and cnrs.witnesses do not yet exist. That RED result is intentional.

During implementation run:

~~~bash
python -m pytest -q acceptance/v014
~~~

Do not weaken or delete an acceptance assertion merely to obtain GREEN. If the contract must change, amend the freeze record through governed change control first.
