from faststream.rabbit import ExchangeType, RabbitExchange, RabbitQueue

exchange = RabbitExchange("delayed", type=ExchangeType.X_DELAYED_MESSAGE, arguments={"x-delayed-type": "direct"})
queue = RabbitQueue("notifications", arguments={"x-max-priority": 5})
