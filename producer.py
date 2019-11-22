from redis import Redis
from redis.exceptions import ResponseError,ConnectionError
from os import environ, urandom
from uuid import uuid1
import random
from time import sleep
from logging import debug, info

'''
This is a generic Redis streams producer. Supply the following as environment variables:
    REDIS_HOSTNAME optional (default localhost)
    REDIS_PORT optional (default 6379)
    REDIS_STREAMNAME
    DELFIRST optional (default:False)
    PAYLOAD optional, size of stream payload to send

    Example:
    $ REDIS_HOSTNAME=localhost; REDIS_PORT=14000; REDIS_STREAMNAME=twitterstream; PAYLOAD=1000000; PORT=8888; python3 producer.py

'''

if __name__ == '__main__':


    redis_hostname = environ.get('REDIS_HOSTNAME','localhost')
    redis_port = environ.get('REDIS_PORT',6379)
    r = Redis(redis_hostname, redis_port,retry_on_timeout=True)

    if 'PAYLOAD' in environ:
        payload = urandom(int(environ.get('PAYLOAD'))) 
    else:
        payload = urandom(1000) 
        payload = urandom()
    
    if 'REDIS_STREAMNAME' in environ:
        stream_key = environ.get('REDIS_STREAMNAME')
    else:
        print("No stream name specified. Please add REDIS_STREAMNAME to your environment vars.")
        exit()

    producer_name = environ.get('USER','user')+":"+environ.get('TERM_SESSION_ID','producer')

    if 'DELFIRST' in environ: 
        print("Stream emptied first: {}".format(r.xtrim(stream_key,0,approximate=False)))

    if 'DEBUG' in environ:
        print("-- Redis host name: "+redis_hostname)
        print("-- Redis port: "+redis_port)
        print("-- Redis stream name: "+stream_key)
        print("-- Producer name: "+producer_name)
        print("-- Payload (KBytes): "+payload/1000)

    count = 0
    while True:
        myuuid = uuid1()
        try:
            if 'DEBUG' in environ:
                print(r.xadd(stream_key, {str(producer_name+":"+str(count)):str(myuuid),"payload":payload}),end="",flush=True) 
            else:
                r.xadd(stream_key, {str(producer_name+":"+str(count)):str(myuuid),"payload":payload})
        except ConnectionError as e:
            print("ConnectionError: sleeping 0.5s")
            sleep(0.5)
            #continue
        print(".", end="",flush=True)
        count=count+1
        if (count % 100 == 0):
            print("Sent {} records".format(count))
        #sleep(random.uniform(0.02,0.9))  # sleep for between 20ms and 0.9s

