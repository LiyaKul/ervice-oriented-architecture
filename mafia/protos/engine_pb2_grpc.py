# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import engine_pb2 as engine__pb2


class EngineServerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Join = channel.unary_unary(
                '/EngineServer/Join',
                request_serializer=engine__pb2.JoinRequest.SerializeToString,
                response_deserializer=engine__pb2.JoinResponse.FromString,
                )
        self.GetPlayers = channel.unary_unary(
                '/EngineServer/GetPlayers',
                request_serializer=engine__pb2.GetPlayersRequest.SerializeToString,
                response_deserializer=engine__pb2.GetPlayersResponse.FromString,
                )
        self.Start = channel.unary_unary(
                '/EngineServer/Start',
                request_serializer=engine__pb2.StartRequest.SerializeToString,
                response_deserializer=engine__pb2.StartResponse.FromString,
                )
        self.GameInfo = channel.unary_stream(
                '/EngineServer/GameInfo',
                request_serializer=engine__pb2.InfoRequest.SerializeToString,
                response_deserializer=engine__pb2.InfoResponse.FromString,
                )
        self.GameAction = channel.stream_stream(
                '/EngineServer/GameAction',
                request_serializer=engine__pb2.ActionRequest.SerializeToString,
                response_deserializer=engine__pb2.ActionResponse.FromString,
                )


class EngineServerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Join(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetPlayers(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Start(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GameInfo(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GameAction(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_EngineServerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Join': grpc.unary_unary_rpc_method_handler(
                    servicer.Join,
                    request_deserializer=engine__pb2.JoinRequest.FromString,
                    response_serializer=engine__pb2.JoinResponse.SerializeToString,
            ),
            'GetPlayers': grpc.unary_unary_rpc_method_handler(
                    servicer.GetPlayers,
                    request_deserializer=engine__pb2.GetPlayersRequest.FromString,
                    response_serializer=engine__pb2.GetPlayersResponse.SerializeToString,
            ),
            'Start': grpc.unary_unary_rpc_method_handler(
                    servicer.Start,
                    request_deserializer=engine__pb2.StartRequest.FromString,
                    response_serializer=engine__pb2.StartResponse.SerializeToString,
            ),
            'GameInfo': grpc.unary_stream_rpc_method_handler(
                    servicer.GameInfo,
                    request_deserializer=engine__pb2.InfoRequest.FromString,
                    response_serializer=engine__pb2.InfoResponse.SerializeToString,
            ),
            'GameAction': grpc.stream_stream_rpc_method_handler(
                    servicer.GameAction,
                    request_deserializer=engine__pb2.ActionRequest.FromString,
                    response_serializer=engine__pb2.ActionResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'EngineServer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class EngineServer(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Join(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/EngineServer/Join',
            engine__pb2.JoinRequest.SerializeToString,
            engine__pb2.JoinResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetPlayers(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/EngineServer/GetPlayers',
            engine__pb2.GetPlayersRequest.SerializeToString,
            engine__pb2.GetPlayersResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Start(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/EngineServer/Start',
            engine__pb2.StartRequest.SerializeToString,
            engine__pb2.StartResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GameInfo(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/EngineServer/GameInfo',
            engine__pb2.InfoRequest.SerializeToString,
            engine__pb2.InfoResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GameAction(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(request_iterator, target, '/EngineServer/GameAction',
            engine__pb2.ActionRequest.SerializeToString,
            engine__pb2.ActionResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
