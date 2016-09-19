# from unittest import *
import re
import fsm
import pytest

def test_operator():
    CONCAT = fsm.Operator('+')
    assert repr(CONCAT) == '+'

def test_regex_to_regextree():
    pass

if __name__ == '__main__':
    pytest.main()