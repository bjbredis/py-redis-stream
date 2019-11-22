# Readme

Usage: Create a python3 virtual environment, install the requirements in requirements.txt

## Producer  
```
STREAM=mystream; PORT=12000; END=10;
for i in $(seq 1 $END); 
    do redis-cli -p $PORT xadd $STREAM "*" key$i `gdate +%s.%N`> /dev/null 2>&1; done
```


## Producer v2
```
export REDIS_HOSTNAME=localhost; export REDIS_PORT=14000; export REDIS_STREAMNAME=mystream; export DELFIRST=TRUE; export PAYLOAD=1000000; export DEBUG=TRUE; 
python3 producer.py
```

## Run the consumer
```
export REDIS_HOSTNAME=localhost; export REDIS_PORT=6379; export REDIS_STREAMNAME=mystream; export  DELFIRST=TRUE; export APP_PORT=8888; export DEBUG=true;  
python3 consumer.py
```

# availability test

```
redis-cli -h $HOST -p $PORT flushall; while true; do redis-cli -h $HOST -p $PORT xadd $STREAM "*" key$i `date +%s.%N`; sleep 1s; done
```

## Docker helper scripts / commands
docker run -d --cap-add sys_resource -h rp1_node1 --name rp1_node1 -p 18443:8443 -p 19443:9443 -p 14000-14005:12000-12005 redislabs/redis:5.4.6-11

docker exec -d --privileged rp1_node1 "/opt/redislabs/bin/rladmin" cluster create name cluster1.local username b@rl.com password <pass>

curl -u b@rl.com:<pass> -k https://localhost:19443/v1/bdbs -X POST -H "Content-Type: application/json" -d '{"name":"src","port":12000,"type":"redis","memory_size":100000000}'
curl -u b@rl.com:<pass> -k https://localhost:19443/v1/bdbs -X POST -H "Content-Type: application/json" -d '{"name":"dest","port":12001,"type":"redis","memory_size":100000000}'


