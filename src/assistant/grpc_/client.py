"""
gRPC Assistant client.
"""
from assistant.assistant_pb2_grpc import AssistantStub
from utils.grpc.client import AsyncGrpcClient
from utils.grpc.client import GrpcClient


class AssistantGrpcClient(GrpcClient):
    class Meta:
        stub = AssistantStub


class AssistantAsyncGrpcClient(AsyncGrpcClient):
    class Meta:
        stub = AssistantStub
