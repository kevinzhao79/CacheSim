FROM ubuntu:22.04
RUN apt-get update
RUN apt-get install -y unzip python3 python3-pip
RUN pip3 install grpcio==1.60.1 grpcio-tools==1.60.1
COPY server.py /
COPY mathdb_pb2.py /
COPY mathdb_pb2_grpc.py /
COPY client.py /
CMD ["python3", "server.py"]
