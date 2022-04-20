Simple load balancer based on ZeroMQ that can distribute compute tasks over multiple workers. It can be used for example to batch training models on GPU cards that are installed on the local machine or over the network.

Inspired by [Load balancing broker](https://zguide.zeromq.org/docs/chapter3/#A-Load-Balancing-Message-Broker) pattern from ZeroMQ documentation.



## Usage

1. Start broker

```
python broker.py
```

Broker is responsible for managing the workers (added worker, worker killed, job finished etc.), and balancing the jobs to the workers.

2. Start one or more parallel workers

```
python worker.py
```

The worker will register itself to the broker.

3. Submit a job

You can evaluate any shell program using the client.py.

```
python client.py COMMAND-TO-EXECUTE
```

This will submit the job to the broker, which will run it on one of the workers.

For example,

* simple shell command

```
python client.py sleep 5
```

* python program:

```
python client.py 'python -c "import time; time.sleep(5)"'
```

## Ressources

https://hanxiao.io/2019/01/02/Serving-Google-BERT-in-Production-using-Tensorflow-and-ZeroMQ/


