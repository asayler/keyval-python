# Andy Sayler

ECHO = @echo

PYTHON = python
PIP = pip
PYLINT = pylint
PYLINT_OPTIONS = --disable=all --enable=E,W --reports=n

REQUIRMENTS = requirments.txt

UNITTEST_PATTERN = '*_tests.py'
UNITTEST_DIRECTORY = "./tests"

PYTHONPATH = $(shell readlink -f ./)
EXPORT_PATH = export PYTHONPATH="$(PYTHONPATH)"

COGS = cogs

.PHONY: all test clean

all:
	$(ECHO) "This is a python project; nothing to build!"

reqs: $(REQUIRMENTS)
	$(PIP) install -r "$<" -U

test:
	$(EXPORT_PATH) && $(PYTHON) -m unittest discover -v -p $(UNITTEST_PATTERN) -s $(UNITTEST_DIRECTORY)

lint:
	-$(EXPORT_PATH) && cd $(UNITTEST_DIRECTORY) && $(PYLINT) $(PYLINT_OPTIONS) *.py
	-$(EXPORT_PATH) && $(PYLINT) $(PYLINT_OPTIONS) keyval

clean:
	$(RM) tests/*.pyc
	$(RM) tests/*~
	$(RM) keyval/*.pyc
	$(RM) keyval/*~
	$(RM) *~
