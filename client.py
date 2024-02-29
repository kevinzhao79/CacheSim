import sys
import threading
import grpc

import mathdb_pb2 as pb2
import mathdb_pb2_grpc as pb2_grpc

#global vars, protected by locks
hits = 0
total = 0

def task(filepath, stub, lock):

    global hits
    global total

    with open(filepath, 'r') as f:
        for line in f:
            command = line.strip().split(',')

            #skip first line
            if (command[0] == 'operation'):
                continue

            match command[0]:
                case 'set':
                    req = pb2.SetRequest(key=command[1], value=float(command[2]))
                    resp = stub.Set(req)
                    error = resp.error

                case 'get':
                    req = pb2.GetRequest(key=command[1])
                    resp = stub.Get(req)
                    value, error = resp.value, resp.error

                case 'add':
                    req = pb2.BinaryOpRequest(key_a=command[1], key_b=command[2])
                    resp = stub.Add(req)
                    value, hit, error = resp.value, resp.cache_hit, resp.error

                    with lock:
                        if (hit):
                            hits += 1
                        total += 1

                case 'sub':
                    req = pb2.BinaryOpRequest(key_a=command[1], key_b=command[2])
                    resp = stub.Sub(req)
                    value, hit, error = resp.value, resp.cache_hit, resp.error
                    
                    with lock:
                        if (hit):
                            hits += 1
                        total += 1

                case 'mult':
                    req = pb2.BinaryOpRequest(key_a=command[1], key_b=command[2])
                    resp = stub.Mult(req)
                    value, hit, error = resp.value, resp.cache_hit, resp.error
                    
                    with lock:
                        if (hit):
                            hits += 1
                        total += 1

                case 'div':
                    req = pb2.BinaryOpRequest(key_a=command[1], key_b=command[2])
                    resp = stub.Div(req)
                    value, hit, error = resp.value, resp.cache_hit, resp.error
                    
                    with lock:
                        if (hit):
                            hits += 1
                        total += 1

                case _:
                    print("Error: could not read contents of command: " + str(command))

            if (error != ""):
                print(error)


def main():

    if (len(sys.argv) < 3):
        print("Usage: python3 client.py <PORT> <THREAD1-WORK.csv> <THREAD2-WORK.csv> <THREAD3-WORK.csv> ...")
        exit(1)
    
    lock = threading.Lock()
    port = str(sys.argv[1])
    forward = '127.0.0.1:' + port
    threads = []
    channel = grpc.insecure_channel(forward)
    stub = pb2_grpc.MathDbStub(channel)

    for i in range(2, len(sys.argv)):
        fp = sys.argv[i]
        threads.append(threading.Thread(target=task, args=(fp, stub, lock)))

    for thread in threads:

        thread.start()
        thread.join()

    if (total == 0):
        print("Error: requests not parsed")
    else:
        print("Hits: {} Total: {}".format(hits, total))
        print(hits/total)
    
main()