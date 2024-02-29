import threading
import traceback

import mathdb_pb2
import mathdb_pb2_grpc
import grpc
from concurrent import futures

class MathCache:

    def __init__(self):
        self.d = {}
        self.LRU = [] #element is a tuple containing [key, # accesses since key was last hit]
        self.size = 0
        self.lock = threading.Lock()

################# BEGIN CACHE FUNCTIONALITY ###################

    def Set(self, key, value):
        #print("set")

        if not key:
            raise KeyError

        self.lock.acquire()
        try:
            self.LRU.clear()
            self.size = 0

            self.d[key] = value
        finally:
            self.lock.release()

    def Get(self, key):
        #print("get")

        if not key:
            raise KeyError

        self.lock.acquire()
        try:
            return self.d[key]
        finally:
            self.lock.release()

    def Append(self, key):
        #print("append")

        if not key:
            raise KeyError

        self.lock.acquire()
        try:
            if self.size >= 10:
                self.lock.release()
                self.Evict()
                self.lock.acquire()

            for i in range(len(self.LRU)):
                self.LRU[i][1] += 1

            self.LRU.append([key, 0])

            self.size += 1
        finally:
            self.lock.release()

    def Evict(self):
        #print("evict")

        max = 0
        idx = -1

        self.lock.acquire()
        try:
            for i in range(len(self.LRU)):
                if self.LRU[i][1] > max:
                    max = self.LRU[i][1]
                    idx = i

            self.LRU.pop(idx)
        finally:
            self.lock.release()

    def Hit(self, idx):
        #print("hit")

        self.lock.acquire()
        try:
            for i in range(len(self.LRU)):
                if (i != idx):
                    self.LRU[i][1] += 1
                else:
                    self.LRU[i][1] = 0
        finally:
            self.lock.release()

################## END CACHE FUNCTIONALITY #####################

################ BEGIN MATH CACHE OPERATIONS ###################

    def Add(self, key_a, key_b):
        #print("add")

        if (not key_a or not key_b):
            raise KeyError

        k = ["add", key_a, key_b]
        hit = False

        for i in range(len(self.LRU)):
            if (k == self.LRU[i][0]):
                hit = True
                self.Hit(i)
        
        if (not hit):
            self.Append(k)


        r = self.Get(key_a) + self.Get(key_b)

        return r, hit

    def Sub(self, key_a, key_b):
        #print("sub")

        if (not key_a or not key_b):
            raise KeyError

        k = ["sub", key_a, key_b]
        hit = False

        for i in range(len(self.LRU)):
            if (k == self.LRU[i][0]):
                hit = True
                self.Hit(i)
        
        if (not hit):
            self.Append(k)

        r = self.Get(key_a) - self.Get(key_b)

        return r, hit

    def Mult(self, key_a, key_b):
        #print("mult")

        if (not key_a or not key_b):
            raise KeyError

        k = ["mult", key_a, key_b]
        hit = False

        for i in range(len(self.LRU)):
            if (k == self.LRU[i][0]):
                hit = True
                self.Hit(i)
        
        if (not hit):
            self.Append(k)

        r = self.Get(key_a) * self.Get(key_b)

        return r, hit

    def Div(self, key_a, key_b):
        #print("div")

        if (not key_a or not key_b):
            raise KeyError

        k = ["div", key_a, key_b]
        hit = False

        for i in range(len(self.LRU)):
            if (k == self.LRU[i][0]):
                hit = True
                self.Hit(i)
        
        if (not hit):
            self.Append(k)

        r = self.Get(key_a) / self.Get(key_b)

        return r, hit

################# END MATH CACHE OPERATIONS ####################

###################### END MATH CACHE  #########################

class MathDb (mathdb_pb2_grpc.MathDbServicer):

    def __init__(self):
        self.cache = MathCache()

    def Set(self, request, context):

        try:
            error = ""
            self.cache.Set(request.key, request.value)
        except(Exception):
            error = str(traceback.format_exc())
        finally:
            return mathdb_pb2.SetResponse(error=error)

    def Get(self, request, context):
        try:
            error = ""
            value = self.cache.Get(request.key)
        except(Exception):
            value = 0
            error = str(traceback.format_exc())
        finally:
            return mathdb_pb2.GetResponse(value=value, error=error)

    def Add(self, request, context):
        try:
            error = ""
            value, hit = self.cache.Add(request.key_a, request.key_b)
        except(Exception):
            value, hit = 0, False
            error = str(traceback.format_exc())
        finally:
            return mathdb_pb2.BinaryOpResponse(value=value, cache_hit=hit, error=error)

    def Sub(self, request, context):
        try:
            error = ""
            value, hit = self.cache.Sub(request.key_a, request.key_b)
        except(Exception):
            value, hit = 0, False
            error = str(traceback.format_exc())
        finally:
            return mathdb_pb2.BinaryOpResponse(value=value, cache_hit=hit, error=error)

    def Mult(self, request, context):
        try:
            error = ""
            value, hit = self.cache.Mult(request.key_a, request.key_b)
        except(Exception):
            value, hit = 0, False
            error = str(traceback.format_exc())
        finally:
            return mathdb_pb2.BinaryOpResponse(value=value, cache_hit=hit, error=error)

    def Div(self, request, context):
        try:
            error = ""
            value, hit = self.cache.Div(request.key_a, request.key_b)
        except(Exception):
            value, hit = 0, False
            error = str(traceback.format_exc())
        finally:
            return mathdb_pb2.BinaryOpResponse(value=value, cache_hit=hit, error=error)

if __name__ == "__main__":

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4), options=(('grpc.so_reuseport', 0),))
    mathdb_pb2_grpc.add_MathDbServicer_to_server(MathDb(), server)
    server.add_insecure_port("[::]:5440", )
    server.start()
    server.wait_for_termination()