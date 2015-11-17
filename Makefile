# Andy Sayler

ECHO = @echo

PYTHON = python
PIP = pip
PYTHON2 = python2
PIP2 = pip2
PYTHON3 = python3
PIP3 = pip3

PYLINT = pylint
PYLINT_OPTIONS = --disable=all --enable=E,W --reports=n

REQUIRMENTS = requirments.txt

UNITTEST_PATTERN = '*_tests.py'
UNITTEST_DIRECTORY = "./tests"

PYTHONPATH = $(shell readlink -f ./)
EXPORTPATH = export PYTHONPATH="$(PYTHONPATH)"

COGS = cogs

.PHONY: all reqs tests reqs2 tests2 reqs3 tests3 clean

all:
	$(ECHO) "This is a python project; nothing to build!"

reqs: $(REQUIRMENTS)
	$(PIP) --version
	$(PIP) install -r "$<" -U

tests:
	$(PYTHON) --version
	$(EXPORTPATH) && $(PYTHON) -m unittest discover -v -p $(UNITTEST_PATTERN) -s $(UNITTEST_DIRECTORY)

reqs2: $(REQUIRMENTS)
	$(PIP2) install -r "$<" -U

tests2:
	$(EXPORTPATH) && $(PYTHON2) -m unittest discover -v -p $(UNITTEST_PATTERN) -s $(UNITTEST_DIRECTORY)

reqs3: $(REQUIRMENTS)
	$(PIP3) install -r "$<" -U

tests3:
	$(EXPORTPATH) && $(PYTHON3) -m unittest discover -v -p $(UNITTEST_PATTERN) -s $(UNITTEST_DIRECTORY)

lint:
	-$(EXPORT_PATH) && cd $(UNITTEST_DIRECTORY) && $(PYLINT) $(PYLINT_OPTIONS) *.py
	-$(EXPORT_PATH) && $(PYLINT) $(PYLINT_OPTIONS) keyval

clean:
	$(RM) tests/*.pyc
	$(RM) tests/*~
	$(RM) keyval/*.pyc
	$(RM) keyval/*~
	$(RM) *~
