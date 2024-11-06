"""
Assistant manager gPRC client.
"""
from bot.bot_pb2_grpc import TelegramBotStub
from utils.grpc.client import AsyncGrpcClient
from utils.grpc.client import GrpcClient


class TelegramBotGrpcClient(GrpcClient):
    class Meta:
        stub = TelegramBotStub


class TelegramBotAsyncGrpcClient(AsyncGrpcClient):
    class Meta:
        stub = TelegramBotStub
