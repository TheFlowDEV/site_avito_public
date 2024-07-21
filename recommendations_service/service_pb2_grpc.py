# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import service_pb2 as service__pb2


class RecommendationsStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.UpdateRecommendations = channel.unary_unary(
                '/Recommendations/UpdateRecommendations',
                request_serializer=service__pb2.rec4msg.SerializeToString,
                response_deserializer=service__pb2.Recommendations_list.FromString,
                )
        self.UpdateRecommendationsByCategory = channel.unary_unary(
                '/Recommendations/UpdateRecommendationsByCategory',
                request_serializer=service__pb2.rec4msg_category.SerializeToString,
                response_deserializer=service__pb2.Recommendations_list.FromString,
                )


class RecommendationsServicer(object):
    """Missing associated documentation comment in .proto file."""

    def UpdateRecommendations(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateRecommendationsByCategory(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RecommendationsServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'UpdateRecommendations': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateRecommendations,
                    request_deserializer=service__pb2.rec4msg.FromString,
                    response_serializer=service__pb2.Recommendations_list.SerializeToString,
            ),
            'UpdateRecommendationsByCategory': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateRecommendationsByCategory,
                    request_deserializer=service__pb2.rec4msg_category.FromString,
                    response_serializer=service__pb2.Recommendations_list.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Recommendations', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Recommendations(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def UpdateRecommendations(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Recommendations/UpdateRecommendations',
            service__pb2.rec4msg.SerializeToString,
            service__pb2.Recommendations_list.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateRecommendationsByCategory(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Recommendations/UpdateRecommendationsByCategory',
            service__pb2.rec4msg_category.SerializeToString,
            service__pb2.Recommendations_list.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
