#!/usr/bin/env python3
import concurrent.futures
import logging
import random
import threading
import time

SENTINEL = -1

class Pipeline():
    '''Class to allow a single element pipeline between producer and consumer.
    '''
    def __init__(self):
        self.value = 0
        self._set_lock = threading.Lock()
        self._get_lock = threading.Lock()
        self._get_lock.acquire()

    def get_value(self, name):
        # name = threading.current_thread().name
        logging.debug(f"{name}:about to acquire getlock")
        self._get_lock.acquire()
        logging.debug(f"{name}:have getlock")
        value = self.value
        logging.debug(f"{name}:about to release setlock")
        self._set_lock.release()
        logging.debug(f"{name}:setlock released")
        return value

    def set_value(self, value, name):
        # name = threading.current_thread().name
        logging.debug(f"{name}:about to acquire setlock")
        self._set_lock.acquire()
        logging.debug(f"{name}:have setlock")
        self.value = value
        logging.debug(f"{name}:about to release getlock")
        self._get_lock.release()
        logging.debug(f"{name}:getlock released")



def producer(pipeline):
    '''Pretend we're getting a number from the network.'''
    for index in range(10):
        new_datapoint = random.randint(1,101)
        logging.warning(f"Producer got data {new_datapoint}")
        pipeline.set_value(new_datapoint, "Producer")

    # send a sentinel value to tell consumer we're done
    pipeline.set_value(SENTINEL, "Producer")



def consumer(pipeline):
    ''' Pretend we're saving a number in the database. '''
    datapoint = 0
    while datapoint != SENTINEL:
        datapoint = pipeline.get_value("Consumer")
        if datapoint != SENTINEL:
            logging.warning(f"Consumer storing data: {datapoint}")


if __name__ == "__main__":
    # FORMAT = '%(asctime)-15s %(message)s'
    FORMAT = '%(message)s'
    logging.basicConfig(format=FORMAT)
    # logging.getLogger().setLevel(logging.DEBUG)

    pipeline = Pipeline()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(producer, pipeline)
        executor.submit(consumer, pipeline)
