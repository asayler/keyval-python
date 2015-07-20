# Andy Sayler
# Summer 2014
# Univerity of Colorado

ECHO = @echo

PYTHON = python
PIP = pip
PYLINT = pylint

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

clean:
	$(RM) tests/*.pyc
	$(RM) tests/*~
	$(RM) keyval/*.pyc
	$(RM) keyval/*~
	$(RM) *~
