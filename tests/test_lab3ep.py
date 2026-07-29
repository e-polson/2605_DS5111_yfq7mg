"""Tests for tracking environment conditions and ID check execution."""

import io
import os
import platform
import sys
import pytest

# Dynamically patch sys.path so Pylint and Python can resolve clean_ids
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../bin")))

# pylint: disable=wrong-import-position, import-error
from clean_ids import main


def run_script_with_input(monkeypatch, capsys, input_data):
    """Helper function for stdin and stdout"""
    fake_input = io.StringIO(input_data)
    monkeypatch.setattr(sys, "stdin", fake_input)
    main()
    return capsys.readouterr().out


def test_os_is_ubuntu():
    """Verifies that the operating system platform is Linux/Ubuntu"""
    assert platform.system() == "Linux"
    assert platform.freedesktop_os_release()["ID"] == "ubuntu"


def test_python_version():
    """Asserts that the environment is running Python 3.14"""
    assert sys.version_info[:2] == (3, 14)


@pytest.mark.xfail(reason="Intentional test failure demo")
def test_that_is_expected_to_fail():
    """An intentional failing assertion tracked as XFAIL"""
    assert False


@pytest.mark.skip(reason="Feature placeholder")
def test_future_feature_placeholder():
    """Skipped test placeholder"""


@pytest.mark.parametrize(
    "input_data,expected_output",
    [
        ("kcFsuxaJ1es\nasd123\n", "kcFsuxaJ1es\n"),  # Original multi-line test
        ("validID1234\n", "validID1234\n"),  # ID must be 11 characters
        ("short\n", ""),  # Too short -> Logs
        ("thisIdIsWayTooLong\n", ""),  # Too long -> Logs
        ("special$$$12\n", ""),  # Bad characters -> Logs
    ],
)
def test_check_id_variations(monkeypatch, capsys, input_data, expected_output):
    """Parametrized test checking multiple types of ID structures"""
    output = run_script_with_input(monkeypatch, capsys, input_data)
    assert output == expected_output
