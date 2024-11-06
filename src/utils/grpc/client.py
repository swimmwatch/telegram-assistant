"""
Wrappers for gRPC clients.
"""
import grpc


class BaseGrpcClient:
    class Meta:
        stub: type


class GrpcClient(BaseGrpcClient):
    def __init__(self, addr: str):
        self.channel = grpc.insecure_channel(addr)
        self.stub = self.Meta.stub(self.channel)

    def __del__(self):
        self.channel.close()


class AsyncGrpcClient(BaseGrpcClient):
    def __init__(self, addr: str):
        self.channel = grpc.aio.insecure_channel(addr)
        self.stub = self.Meta.stub(self.channel)

    async def __adel__(self):
        await self.channel.close()
