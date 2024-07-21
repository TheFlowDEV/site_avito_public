FROM python:latest

COPY requirements.txt tmp/requirements.txt
ADD recommendation_server.py /recommendation_service/
ADD service_pb2_grpc.py /recommendation_service/
ADD service_pb2.py /recommendation_service/
ADD service_pb2.pyi /recommendation_service/
RUN python -m pip install -r /tmp/requirements.txt
WORKDIR /recommendation_service/
