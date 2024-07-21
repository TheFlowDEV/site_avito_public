import grpc.aio
from . import service_pb2_grpc,service_pb2
async def update_recommendations(adv_id):
        async with grpc.aio.insecure_channel("localhost:50051") as channel:
            stub = service_pb2_grpc.RecommendationsStub(channel)
            val_future = await stub.UpdateRecommendations(service_pb2.rec4msg_category(adv_id=adv_id))
            return val_future
async def update_recommendations_category(adv_id,category):
        async with grpc.aio.insecure_channel("localhost:50051") as channel:
            stub = service_pb2_grpc.RecommendationsStub(channel)
            val_future = await stub.UpdateRecommendationsByCategory(service_pb2.rec4msg_category(adv_id=adv_id,category=category))
            return val_future