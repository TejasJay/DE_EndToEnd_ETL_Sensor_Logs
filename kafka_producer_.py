import json
import time
import random
from kafka import KafkaProducer

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda x: json.dumps(x).encode('utf-8')  # Convert dict to JSON
)

# Simulate IoT Sensor Data
sensor_ids = ["sensor-01", "sensor-02", "sensor-03", "sensor-04", "sensor-05"]
locations = ["Room A", "Room B", "Warehouse", "Factory Floor", "Outdoor"]
sensor_types = ["Temperature", "Pressure", "Humidity", "Proximity", "Motion"]
device_status = ["active", "inactive", "maintenance", "offline"]

while True:
    data = {
        "sensor_id": random.choice(sensor_ids),
        "temperature": round(random.uniform(20.0, 30.0), 2),
        "pressure": round(random.uniform(900, 1100), 2),
        "humidity": round(random.uniform(30.0, 60.0), 2),
        "battery_level": round(random.uniform(0.0, 100.0), 2),
        "location": random.choice(locations),
        "sensor_type": random.choice(sensor_types),
        "device_status": random.choice(device_status),
        "timestamp": time.time()
    }
    
    producer.send("iot-sensors", data)
    #print(f"Sent: {data}")
    #time.sleep(2)  # Send data every 2 seconds
