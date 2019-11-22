from redis import Redis
from redis.exceptions import ResponseError,ConnectionError
from os import environ
from logging import debug, info
from time import sleep
from flask import Flask

'''
This is a generic Redis streams consumer. Supply the following as environment variables:
    REDIS_HOSTNAME optional (default localhost)
    REDIS_PORT optional (default 6379)
    REDIS_STREAMNAME
    REDIS_CONSUMERGROUPNAME (default cons_group)
    DEBUG optional (boolean, default: False)

    Example:
    $ APP_PORT=8888; REDIS_CONSUMERGROUPNAME=cons_group; REDIS_HOSTNAME=localhost; REDIS_PORT=14000; REDIS_STREAMNAME=twitterstream; python3 consumer.py
'''

app = Flask(__name__)

# Get port from environment variable or choose 888 as local default
app_port = int(environ.get("APP_PORT", 8888)) 

#check VCAP_SERVICES first
if 'VCAP_SERVICES' in environ:
    services = json.loads(environ.get('VCAP_SERVICES'))
    if 'redislabs' in services:
        hostname = services['redislabs'][0]['credentials']['host']
        provider = 'Redis Enterprise'
    else: #if 'redislabs' in services:
        redis_env = services['p-redis'][0]['credentials']
        provider = 'Pivotal OSS Redis'
    # else:
    #     print("Could not find a binded redis in VCAP_SERVICES: {}".format(services))
else:
    #running locally
    redis_hostname = environ.get('REDIS_HOSTNAME','localhost')
    redis_port = environ.get('REDIS_PORT',6379)

#probably should try/except here
r = Redis(host=redis_hostname, port=redis_port,retry_on_timeout=True)

if 'REDIS_STREAMNAME' in environ:
    stream_key = environ.get('REDIS_STREAMNAME')
else:
    print("No stream name specified. Please add REDIS_STREAMNAME to your environment vars.")
    exit()

group_name = environ.get('REDIS_CONSUMERGROUPNAME','cons_group')
consumer_name = environ.get('USER','user')+":"+environ.get('TERM_SESSION_ID','consumer')
stream_offsets = {stream_key: ">"}

if 'DEBUG' in environ:
    print("DEBUG: App port: {}, Redis host/port: {}:{}, stream: {}, cons_group: {}, cons name: {}"
        .format(app_port,redis_hostname,redis_port,stream_key,group_name,consumer_name))

# try this in a loop?
try:
    r.xgroup_destroy(stream_key, group_name)
    r.xgroup_create(stream_key, group_name, id="0-0")
except ResponseError as e:
    print("Group already exists. Continuing.")

@app.route('/')
def get_bigges_delta():
    return render_template('index.html', provider="test")

if __name__ == '__main__':
    # Run the app, listening on all IPs with our chosen port number
    app.run(host='0.0.0.0', port=app_port)
    
    #consider storing last timestamp in a Redis key so that consumers can be added.
    current = last = delta = biggest_delta = 0
    first = True

    while True:
        try:
            result = r.xreadgroup(group_name,consumer_name,stream_offsets,count=1, block=1000)
        except ConnectionError as e:
                print("No redis connection, sleeping 1s")
                sleep(1)
                continue

        if len(result) >= 0:    
            try:
                element = result[0].pop().pop() 
            except IndexError as e:
                print("No new records, sleeping 1s")
                sleep(1)
                continue
            #print("Retrieved key: {}".format(element[0])) 
            epoch = [int(s) for s in element[0].decode('UTF-8').split('-') if s.isdigit()]
            current = epoch[0]
           # print(current,last))
            if first == True: 
                first = False
                delta = 0
            else: 
                delta = (current - last) 
                if delta > biggest_delta:
                    biggest_delta = delta
                    r.zadd("biggest_delta",{str(current):biggest_delta})
                    print("Biggest Delta is: {}ms".format(biggest_delta))
            last = current   
            #print(epoch[0])
        #sleep(0.1)

