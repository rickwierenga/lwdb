import os

import redis
from rq import Worker, Queue, Connection

# needed for some reason, kinda strange but whatever
import sys
sys.path.insert(0, ".")

listen = ["default"]

redis_host = os.environ.get("REDIS_HOST")

if __name__ == "__main__":
  conn = redis.StrictRedis(host=redis_host, port=6379, db=0, decode_responses=False)

  with Connection(conn):
    print("working")
    worker = Worker(list(map(Queue, listen)))
    worker.work()
