# Run pytest locally

# Quick start with bash

Install all the packages by running install_test.sh

```bash
./install_test.sh
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

# Install packages manually

First install all test's packages requirements.
Recommend to install packages in virtual environment
```bash
sudo apt install portaudio19-dev
pip install -r tests/requirements.txt
```