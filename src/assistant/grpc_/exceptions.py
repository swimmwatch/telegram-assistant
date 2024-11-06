"""
Assistant gRPC exceptions.
"""


class BaseAssistantServerException(Exception):
    pass


class ClientIsNotInitiated(BaseAssistantServerException):
    pass


class ClientAlreadyInitiated(BaseAssistantServerException):
    pass
