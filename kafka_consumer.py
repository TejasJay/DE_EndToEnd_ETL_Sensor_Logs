import json
from kafka import KafkaConsumer

# Kafka Consumer
consumer = KafkaConsumer(
    "iot-sensors",
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))  # Convert JSON to dict
)

print("Listening for IoT Sensor Data...")
for message in consumer:
    print(f"Received: {message.value}")
