"""
Unittests for commands.
"""
import typing

import pytest

from assistant.commands.handler import ExplicitCommand
from assistant.commands.types import ParsedArguments


@pytest.mark.parametrize(
    "name",
    [
        r"",
        r"\\",
        r"\c",
        r"c\c",
        r"c\\",
        "a" * ExplicitCommand.MAX_COMMAND_NAME_LEN,
        "1",
        "a1",
        "1a",
    ],
)
def test_command_invalid_name(name: str):
    with pytest.raises(ValueError):  # noqa
        ExplicitCommand(name=name)


@pytest.mark.parametrize(
    ("text", "args", "expected"),
    [
        ("", {}, None),
        ("nam", {}, None),
        ("name", {}, None),
        (r"\name", {}, {}),
        (r" \name", {}, None),
        # Cases with int type
        (r"\name 0", {"param1": int}, {"param1": 0}),
        (r"\name -1", {"param1": int}, {"param1": -1}),
        (r"\name 123", {"param1": int}, {"param1": 123}),
        # Cases with float type
        (r"\name 0.0", {"param1": float}, {"param1": 0.0}),
        (r"\name -1.0", {"param1": float}, {"param1": -1.0}),
        (r"\name 123.123", {"param1": float}, {"param1": 123.123}),
        # Cases with str types
        (r"\name hello", {"param1": str}, {"param1": "hello"}),
        # Cases with several parameters
        (
            r"\name hello",
            {"param1": str, "param2": str},
            {"param1": "hello", "param2": None},
        ),
        (
            r"\name hello world",
            {"param1": str, "param2": str},
            {"param1": "hello", "param2": "world"},
        ),
        (
            "\\name \n  hello\t  world  ",
            {"param1": str, "param2": str},
            {"param1": "hello", "param2": "world"},
        ),
    ],
)
def test_command_parser_with_immutable_types(
    text: str, args: dict[str, typing.Type], expected: ParsedArguments
):
    name = "name"
    command = ExplicitCommand(name=name)
    for arg_name, arg_type in args.items():
        command.add_arg(arg_name, arg_type)
    actual = command.parse(text)
    assert actual == expected
