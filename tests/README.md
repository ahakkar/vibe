# Run pytest locally

First install all test's packages requirements.
Recommend to install packages in virtual environment
```bash
pip install -r tests/requirements.txt
```

Then run all the tests using pytest
```bash
pytest
```

or

```bash
pytest tests
```

# Run tests by mark

{mark}
unit    -   unit tests
int     -   integration tests
sys     -   system tests
perf    -   performance tests
sec     -   security tests

```bash
pytest -v -m {mark}
```