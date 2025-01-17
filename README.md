## Test task for https://t.me/major

Technical task

<i>
It is necessary to make a queue with priorities for sending messages to tg (aiogram) on rabbitMq and an example of its integration into the aiogram bot and fast api application.

This queue should solve the problem of the rate limit for sending 30 messages per second, the available rate limit should be used to the maximum
</i>

## Solution

The solution is implemented using the following technologies:
 - Python 3.11
 - FastStream+RabbitMQ
 - aiogram
 - FastAPI
 - Docker (Compose)
 - Prometheus
 - Grafana
 - Tempo

## Features
* Exporting traces to **Grafana Tempo** via **gRPC**
* Visualization of traces via **Grafana**
* Collecting metrics and exporting using **Prometheus**
* [**Grafana dashboard**](https://grafana.com/grafana/dashboards/22130-faststream-metrics/) for metrics
* Configured **docker-compose** with the entire infrastructure

## How to run the example

1. Clone project
```shell
git clone https://github.com/sheldygg/major-test-task.git
```
2. Start application
```shell
docker compose --profile exchange --profile grafana up --build -d
```
3. Open **Grafana** on `http://127.0.0.1:3000` with login `admin` and password `admin`
4. Go to **Explore** - **Tempo**
5. Enter TraceQL query `{}`
6. Go to **Dashboards** - **FastStream Metrics**

## How to use
The are three ways
1. **FastAPI** application
```shell
 curl "http://localhost:8811/sendMessage?chat_id=user_id&text=text"
```
2. **aiogram** bot
```
/send_message user_id text
```
3. **Raw publication to queue**

## Trace and metrics examples

![Trace example](https://i.imgur.com/d7UiZMj.png)
![Metrics example](https://i.imgur.com/qFQSe1s.png)
