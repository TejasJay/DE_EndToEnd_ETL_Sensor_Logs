#!/bin/bash

# Function to check if a process is running
is_running() {
    pgrep -f "$1" > /dev/null 2>&1
}

# Start Zookeeper if not running
if is_running "QuorumPeerMain"; then
    echo "Zookeeper is already running."
else
    echo "Starting Zookeeper..."
    ~/kafka/bin/zookeeper-server-start.sh ~/kafka/config/zookeeper.properties & 
    sleep 20
fi

# Start Kafka Broker if not running
if is_running "kafka.Kafka"; then
    echo "Kafka Broker is already running."
else
    echo "Starting Kafka Broker..."
    ~/kafka/bin/kafka-server-start.sh ~/kafka/config/server.properties &
    sleep 20
fi

# Create Kafka Topics (Skip if already exists)
echo "Ensuring Kafka topics exist..."
~/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092 | grep -q "webserver-logs" || \
~/kafka/bin/kafka-topics.sh --create --topic webserver-logs --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

~/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092 | grep -q "app-logs" || \
~/kafka/bin/kafka-topics.sh --create --topic app-logs --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

~/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092 | grep -q "security-logs" || \
~/kafka/bin/kafka-topics.sh --create --topic security-logs --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# Start Log Generators if not running
for script in "generate_logs.py" "generate_app_logs.py" "generate_security_logs.py"; do
    if is_running "$script"; then
        echo "$script is already running."
    else
        echo "Starting $script..."
        python3 ~/DE_prj/$script &
    fi
done

# Start Flume if not running
if is_running "flume-ng"; then
    echo "Flume is already running."
else
    echo "Starting Flume..."
    flume-ng agent --conf ~/DE_prj/conf --conf-file ~/DE_prj/flume-kafka.conf --name agent1 -Dflume.root.logger=INFO,console &
fi

# Start Kafka Producer if not running
if is_running "kafka_producer_.py"; then
    echo "Kafka producer is already running."
else
    echo "Starting Kafka producer..."
    python3 ~/DE_prj/kafka_producer_.py &
fi

echo "All required services are running!"
