# CacheSim
A simulation of an LRU cache hosted on a server, called using gRPC.
Created as a project for CS 544 - Distributed Systems (GitHub: https://github.com/cs544-wisc/s24/tree/main). 

Before running, make sure you have Docker downloaded. This program runs off of Ubuntu's 22.04 LTS Docker Image.

1. Build your .proto file:
python3 -m grpc_tools.protoc -I=. --python_out=. --grpc_python_out=. mathdb.proto

2. Run the server on your terminal in the background:
python3 server.py &

3. Then run the client and specify the files where it sources requests:
python3 client.py <PORT> <THREAD1-WORK.csv> <THREAD2-WORK.csv> <THREAD3-WORK.csv> ...  (Set <PORT> to 5440. to change default port, manually change the .add_insecure_port() channel in server.py.

4.1. To kill the server, run:
lsof -i tcp

4.2. Then find the PID of the program using port 5440, and run:
kill -9 <PID>
