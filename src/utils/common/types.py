"""
Common custom typings.
"""
from contextlib import AbstractAsyncContextManager
from contextlib import AbstractContextManager
from typing import TypeVar

# Context manager
ContextManagerType = TypeVar(
    "ContextManagerType", AbstractContextManager, AbstractAsyncContextManager
)
