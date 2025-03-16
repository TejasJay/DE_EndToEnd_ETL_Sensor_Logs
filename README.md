# **📌 End To End Project to Consume Real-Time Logs of Multiple Systems and IOT Sensor data readings Using Flume, Kafka, MySQL & Looker**

***
## **Architechture of the Project**

<img src="./Note 15 Mar 2025-rotated.jpg" alt="Rotated Note" />


***
## **Demo of the Project**


<div>
    <a href="https://www.loom.com/share/38d9d596ffeb4ef0b344319f4caac600" target="_blank">
      <img style="max-width:600px; width:100%;" src="https://cdn.loom.com/sessions/thumbnails/38d9d596ffeb4ef0b344319f4caac600-d6b98e41f43a5975-full-play.gif">
    </a>
</div>

***

## **📌 Step 0: Setting Up GCP Firewall & VPC for Kafka and MySQL External Access**

Before integrating **Kafka and MySQL with Google Colab**, we need to configure **GCP firewall rules** and **VPC settings** to allow external access. If the services are on **different networks**, they will not be able to communicate, so ensure they are on the **same VPC network**.

* * *

### **🔹 Step 0.1: Configuring GCP Firewall to Allow Kafka Access from Colab**

Since **Kafka runs on port 9093**, we must **open this port** in the firewall so that Google Colab can communicate with it.

#### **🚀 Firewall Rule: Kafka (Port 9093)**

| **Setting** | **Value** |
| --- | --- |
| **Priority** | `100` (Higher priority) |
| **Parent Policy** | `colab-entry` (Ensures rule applies to Colab traffic) |
| **Direction** | `Ingress` (Incoming connections allowed) |
| **Action** | `Allow` (Permit traffic) |
| **Protocols/Ports** | `tcp:9093` (Kafka uses port `9093`) |
| **Target Type** | `Apply to all` (No restriction on which instances are affected) |
| **Source IP** | `0.0.0.0/0` (Allows traffic from any external IP) |

✅ **Why is this needed?**

-   **Kafka brokers** use port **9093** for external clients.
-   **Google Colab is external**, so it must be allowed to connect.
-   **If this rule is missing**, Kafka running on GCP **won't be reachable** from Colab.
* * *

### **🔹 Step 0.2: Configuring GCP Firewall to Allow MySQL Access from Colab**

Since **MySQL runs on port 3306**, we need to open this port so that Google Colab can connect.

#### **🚀 Firewall Rule: MySQL (Port 3306)**

| **Setting** | **Value** |
| --- | --- |
| **Priority** | `1000` (Lower priority than Kafka) |
| **Description** | `Allow MySQL external connections` |
| **Network** | `default` (Ensures MySQL is accessible in the correct VPC) |
| **Direction** | `Ingress` (Allow incoming connections) |
| **Action** | `Allow` (Permit traffic) |
| **Protocols/Ports** | `tcp:3306` (MySQL runs on `3306`) |
| **Source IP** | `0.0.0.0/0` (Allows traffic from any external IP) |

✅ **Why is this needed?**

-   **Google Colab runs externally**, so MySQL must allow incoming connections.
-   If this rule **is missing**, **Colab won’t be able to access MySQL**, leading to **connection timeouts**.
-   **Only authorized users should have access**, so this firewall rule should later be **restricted** to your Colab's **IP range** instead of `0.0.0.0/0`.
* * *

### **🔍 VPC Network Details**

| **Setting** | **Value** |
| --- | --- |
| **Description** | `Default network for the project` |
| **Maximum Transmission Unit (MTU)** | `1460` |
| **ULA IPv6 Range** | `Disabled` |
| **Subnet Mode** | `Auto subnets` |
| **Routing Mode** | `Regional` |
| **Best Path Selection Mode** | `Legacy` |

✅ **Why is this important?**

-   **Kafka and MySQL must be on the same network** (`default`) for internal communication.
-   If they are on **different VPC networks**, they **won’t be able to communicate**.
-   **Subnets must be configured correctly** to avoid cross-region access issues.
* * *

### **📌 Step 0: Executing GCP Firewall Rules via Google Cloud Shell**

To set up the required **firewall rules** for **Kafka (Port 9093) and MySQL (Port 3306)** via **Google Cloud Shell**, run the following commands.

* * *

## **🔹 Step 0.1: Create Firewall Rule for Kafka (Port 9093)**

```bash
gcloud compute firewall-rules create allow-kafka-external \
    --direction=INGRESS \
    --priority=100 \
    --network=default \
    --action=ALLOW \
    --rules=tcp:9093 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=kafka
```

✅ **Explanation:**

-   `gcloud compute firewall-rules create allow-kafka-external` → Creates a firewall rule named **allow-kafka-external**.
-   `--direction=INGRESS` → Allows **incoming** connections.
-   `--priority=100` → Ensures **Kafka has a high-priority rule**.
-   `--network=default` → Ensures the rule applies to the **default VPC network**.
-   `--action=ALLOW` → Allows **incoming traffic**.
-   `--rules=tcp:9093` → Allows **Kafka broker connections**.
-   `--source-ranges=0.0.0.0/0` → Allows **any IP to access Kafka** (**⚠️ Later, restrict this to trusted IPs**).
-   `--target-tags=kafka` → Applies this rule **only to instances with the "kafka" tag**.
* * *

## **🔹 Step 0.2: Create Firewall Rule for MySQL (Port 3306)**

```bash
gcloud compute firewall-rules create allow-mysql-external \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=tcp:3306 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=mysql
```

✅ **Explanation:**

-   `gcloud compute firewall-rules create allow-mysql-external` → Creates a firewall rule named **allow-mysql-external**.
-   `--direction=INGRESS` → Allows **incoming connections**.
-   `--priority=1000` → Lower priority than Kafka (higher number = lower priority).
-   `--network=default` → Applies to the **default VPC**.
-   `--action=ALLOW` → Allows **incoming MySQL connections**.
-   `--rules=tcp:3306` → Allows **MySQL traffic**.
-   `--source-ranges=0.0.0.0/0` → Allows **all IPs** (**⚠️ Should be restricted later**).
-   `--target-tags=mysql` → Applies the rule **only to instances with the "mysql" tag**.
* * *

## **🔍 Verify Firewall Rules**

After executing the above commands, run this to verify that the firewall rules are active:

```bash
gcloud compute firewall-rules list --format="table(name,network,direction,priority,allowed,sourceRanges)"
```

✅ **Expected Output:**

```
NAME                   NETWORK  DIRECTION  PRIORITY  ALLOWED      SOURCE RANGES
allow-kafka-external   default  INGRESS    100       tcp:9093     0.0.0.0/0
allow-mysql-external   default  INGRESS    1000      tcp:3306     0.0.0.0/0
```

* * *

## **🔹 Step 0.3: Apply Firewall Rules to Instances**

If your **Kafka and MySQL instances don’t have the correct network tags**, add them using:

```bash
gcloud compute instances add-tags kafka-instance --tags=kafka
gcloud compute instances add-tags mysql-instance --tags=mysql
```

✅ **Replace**:

-   `kafka-instance` → Your actual **Kafka VM name**.
-   `mysql-instance` → Your actual **MySQL VM name**.
* * *

## **📌 Step 1: Consuming Logs - Writing Python Scripts to Simulate Logs**

In this step, we **generate synthetic log files** to simulate logs from three different sources:

1.  **Web Server Logs (`generate_logs.py`)**
2.  **Application Logs (`generate_app_logs.py`)**
3.  **Security Logs (`generate_security_logs.py`)**

These logs will later be **streamed into Kafka**, processed, and stored in **MySQL for analysis**.

* * *

### **📌 Step 1.1: Understanding the Python Log Generators**

We have **three separate Python scripts**, each writing logs to a specific file.

* * *

## **1️⃣ Web Server Logs (`generate_logs.py`)**

This script **simulates HTTP access logs** similar to **Nginx/Apache logs**.

### **🔍 Breakdown of Code**

```python
import time
import random
import uuid
```

-   **Imports Required Modules:**
    -   `time` → Used for delays in log generation.
    -   `random` → Generates **random IP addresses and byte sizes**.
    -   `uuid` → Creates a **session ID** that persists for **5 minutes**.
* * *

```python
session_id = str(uuid.uuid4())[:8]
start_time = time.time()
```

-   **Session ID** is generated using `uuid4()` and stored as an **8-character string**.
-   This **ID remains the same for 5 minutes** to simulate a real session.
* * *

```python
log_format = '{session_id} {ip} - - [{timestamp}] "GET /index.html HTTP/1.1" 200 {bytes}'
```

-   Defines **log format** similar to Apache/Nginx:

    ```
    session_id IP - - [timestamp] "GET /index.html HTTP/1.1" 200 <random_bytes>
    ```

* * *

```python
with open("webserver_logs.txt", "a") as log_file:
```

-   Opens a **file in append mode (`"a"`)** to continuously write logs.
* * *

```python
if time.time() - start_time > 300:
    session_id = str(uuid.uuid4())[:8]
    start_time = time.time()
```

-   Every **5 minutes (300 seconds)**, a **new session ID is generated**.
* * *

```python
log_entry = log_format.format(
    session_id=session_id,
    ip=f"192.168.1.{random.randint(1, 255)}",
    timestamp=time.strftime("%d/%b/%Y:%H:%M:%S +0000"),
    bytes=random.randint(500, 5000)
)
```

-   Generates **randomized log data**:
    -   IP address (`192.168.1.X`)
    -   Timestamp (`DD/Mon/YYYY:HH:MM:SS +0000`)
    -   Random **byte size** (500 - 5000)

✅ **Example Output (webserver\_logs.txt)**

```
3f2a1d8e 192.168.1.23 - - [14/Mar/2025:14:30:21 +0000] "GET /index.html HTTP/1.1" 200 2312
```

* * *

```python
log_file.write(log_entry + "\n")
log_file.flush()
time.sleep(2)
```

-   Writes **log entry to the file**.
-   Uses **`flush()`** to immediately save data.
-   **Sleeps for 2 seconds** before generating the next log.
* * *

## **2️⃣ Application Logs (`generate_app_logs.py`)**

This script **simulates application-level logs**, including:

-   **Database connections**
-   **API requests**
-   **Server timeouts**
-   **Authentication events**

### **🔍 Breakdown of Code**

```python
app_log_levels = ["INFO", "WARN", "ERROR", "DEBUG"]
log_format = '{session_id} [{timestamp}] {log_level} - {message}'
```

-   Defines possible **log levels** (`INFO`, `WARN`, `ERROR`, `DEBUG`).
-   Log format follows a standard **application log structure**:

    ```
    session_id [timestamp] LOG_LEVEL - message
    ```

* * *

```python
messages = [
    "User logged in",
    "Database connection successful",
    "API request processed",
    "Cache miss for user profile",
    "Server timeout on request",
    "Data sync started",
    "Failed to fetch user details",
    "Payment transaction completed"
]
```

-   Predefined **random messages** to simulate different application events.
* * *

```python
with open("app_logs.txt", "a") as log_file:
```

-   Opens **application log file** in **append mode**.
* * *

```python
if time.time() - start_time > 300:
    session_id = str(uuid.uuid4())[:8]
    start_time = time.time()
```

-   **Generates a new session ID every 5 minutes**.
* * *

```python
log_entry = log_format.format(
    session_id=session_id,
    timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
    log_level=random.choice(app_log_levels),
    message=random.choice(messages)
)
```

-   Generates **randomized log data**:
    -   Log level (`INFO`, `WARN`, `ERROR`, `DEBUG`)
    -   **Timestamp** (`YYYY-MM-DD HH:MM:SS`)
    -   **Message** (e.g., `"API request processed"`)

✅ **Example Output (app\_logs.txt)**

```
3f2a1d8e [2025-03-14 15:20:30] INFO - User logged in
```

* * *

```python
log_file.write(log_entry + "\n")
log_file.flush()
time.sleep(2)
```

-   Writes log **to file** and **waits 2 seconds** before the next log.
* * *

## **3️⃣ Security Logs (`generate_security_logs.py`)**

This script **simulates security-related logs**, including:

-   **Unauthorized access**
-   **Firewall rule changes**
-   **SSH access attempts**
-   **Intrusion detection events**

### **🔍 Breakdown of Code**

```python
security_events = [
    "Unauthorized login attempt",
    "Firewall rule updated",
    "SSH access granted",
    "Intrusion detected",
    "User account locked due to failed login attempts",
    "Security patch applied",
    "Malware scan completed"
]
```

-   Predefined **random security event messages**.
* * *

```python
log_format = '{session_id} [{timestamp}] SECURITY - {event}'
```

-   Log format:

    ```
    session_id [timestamp] SECURITY - event
    ```

* * *

```python
if time.time() - start_time > 300:
    session_id = str(uuid.uuid4())[:8]
    start_time = time.time()
```

-   **New session ID every 5 minutes**.
* * *

```python
log_entry = log_format.format(
    session_id=session_id,
    timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
    event=random.choice(security_events)
)
```

-   Generates **randomized security log data**.

✅ **Example Output (security\_logs.txt)**

```
3f2a1d8e [2025-03-14 15:25:12] SECURITY - Unauthorized login attempt
```

* * *

```python
log_file.write(log_entry + "\n")
log_file.flush()
time.sleep(3)
```

-   Writes **security log** and waits **3 seconds** before generating the next one.
* * *

## **📌 Summary**

| **Log Type** | **File Name** | **Log Frequency** | **Key Fields** |
| --- | --- | --- | --- |
| Web Server Logs | `webserver_logs.txt` | Every **2 seconds** | Session ID, IP, Bytes, HTTP Status |
| Application Logs | `app_logs.txt` | Every **2 seconds** | Log Level, Message, Timestamp |
| Security Logs | `security_logs.txt` | Every **3 seconds** | Security Event, Timestamp |

* * *

## **📌 Step 1.2: Using Apache Flume to Stream Logs to Kafka in Real-Time**

Now that **Python scripts** are generating logs into text files (`.txt`), the next step is to **consume these logs using Apache Flume** and stream them to **Kafka topics**.

🔹 **Why Use Flume?**

-   **Continuously monitors (`tail -F`) log files** and ingests new log entries.
-   **Streams logs in real-time** from multiple sources (web, app, security).
-   **Buffers logs using channels** before forwarding them to Kafka.
-   **Efficiently batches and transports log data** to Kafka for further processing.
* * *

## **🔍 Understanding `flume-kafka.conf` Configuration**

This configuration defines:

-   **Sources** → Reads logs from text files.
-   **Channels** → Buffers logs before sending them to Kafka.
-   **Sinks** → Sends logs to Kafka topics.
* * *

### **🔹 Step 1: Define Sources (Reading Logs from Files)**

```properties
agent1.sources = source1 source2 source3
```

-   Defines **three sources** (`source1`, `source2`, `source3`) for **Web Server, Application, and Security logs**.

#### **1️⃣ Web Server Logs Source**

```properties
agent1.sources.source1.type = exec
agent1.sources.source1.command = tail -F /home/tejasjay94/DE_prj/webserver_logs.txt
agent1.sources.source1.channels = channel1
```

✅ **What It Does:**

-   Uses **`exec` source type** to **execute a shell command**.
-   Runs `tail -F` to **follow (`-F`) `webserver_logs.txt`** and capture new log entries.
-   Sends logs to **`channel1`** for further processing.

#### **2️⃣ Application Logs Source**

```properties
agent1.sources.source2.type = exec
agent1.sources.source2.command = tail -F /home/tejasjay94/DE_prj/app_logs.txt
agent1.sources.source2.channels = channel2
```

✅ **What It Does:**

-   Reads `app_logs.txt` in real-time.
-   Uses `channel2` to buffer logs before sending them to Kafka.

#### **3️⃣ Security Logs Source**

```properties
agent1.sources.source3.type = exec
agent1.sources.source3.command = tail -F /home/tejasjay94/DE_prj/security_logs.txt
agent1.sources.source3.channels = channel3
```

✅ **What It Does:**

-   Reads `security_logs.txt` for new security logs.
-   Sends logs to **`channel3`**.
* * *

### **🔹 Step 2: Define Kafka Sinks (Streaming Logs to Kafka Topics)**

```properties
agent1.sinks = sink1 sink2 sink3
```

-   Defines **three sinks** (`sink1`, `sink2`, `sink3`).
-   Each sink sends logs to a **Kafka topic**.

#### **1️⃣ Web Server Logs Sink**

```properties
agent1.sinks.sink1.type = org.apache.flume.sink.kafka.KafkaSink
agent1.sinks.sink1.brokerList = localhost:9092
agent1.sinks.sink1.kafka.topic = webserver-logs
agent1.sinks.sink1.kafka.flumeBatchSize = 20
agent1.sinks.sink1.channel = channel1
agent1.sinks.sink1.serializer = org.apache.flume.sink.kafka.KafkaAvroSerializer
```

✅ **What It Does:**

-   Uses **`KafkaSink`** to send logs to Kafka.
-   **`brokerList = localhost:9092`** → Sends logs to Kafka running on port `9092`.
-   **`kafka.topic = webserver-logs`** → Web server logs are published to `webserver-logs` topic.
-   **`flumeBatchSize = 20`** → Sends logs in batches of **20 messages** for efficiency.
-   **Uses `KafkaAvroSerializer`** for **serialization before sending to Kafka**.

#### **2️⃣ Application Logs Sink**

```properties
agent1.sinks.sink2.type = org.apache.flume.sink.kafka.KafkaSink
agent1.sinks.sink2.brokerList = localhost:9092
agent1.sinks.sink2.kafka.topic = app-logs
agent1.sinks.sink2.kafka.flumeBatchSize = 20
agent1.sinks.sink2.channel = channel2
agent1.sinks.sink2.serializer = org.apache.flume.sink.kafka.KafkaAvroSerializer
```

✅ **What It Does:**

-   Publishes logs to **Kafka topic: `app-logs`**.
-   Uses `KafkaAvroSerializer` for structured serialization.

#### **3️⃣ Security Logs Sink**

```properties
agent1.sinks.sink3.type = org.apache.flume.sink.kafka.KafkaSink
agent1.sinks.sink3.brokerList = localhost:9092
agent1.sinks.sink3.kafka.topic = security-logs
agent1.sinks.sink3.kafka.flumeBatchSize = 20
agent1.sinks.sink3.channel = channel3
agent1.sinks.sink3.serializer = org.apache.flume.sink.kafka.KafkaAvroSerializer
```

✅ **What It Does:**

-   Streams security logs to Kafka topic **`security-logs`**.
-   Uses **batching** for efficiency.
* * *

### **🔹 Step 3: Define Flume Channels (Temporary Buffer for Logs)**

```properties
agent1.channels = channel1 channel2 channel3
```

-   Defines **three memory-based channels** to buffer logs **before forwarding**.

#### **1️⃣ Web Server Logs Channel**

```properties
agent1.channels.channel1.type = memory
agent1.channels.channel1.capacity = 1000
agent1.channels.channel1.transactionCapacity = 100
```

✅ **What It Does:**

-   **Stores up to 1000 logs** in memory before sending to Kafka.
-   Processes **100 logs per transaction**.

#### **2️⃣ Application Logs Channel**

```properties
agent1.channels.channel2.type = memory
agent1.channels.channel2.capacity = 1000
agent1.channels.channel2.transactionCapacity = 100
```

✅ **What It Does:**

-   Buffers **application logs** in memory.

#### **3️⃣ Security Logs Channel**

```properties
agent1.channels.channel3.type = memory
agent1.channels.channel3.capacity = 1000
agent1.channels.channel3.transactionCapacity = 100
```

✅ **What It Does:**

-   Buffers **security logs** in memory before forwarding.
* * *

## **📌 Running the Flume Agent**

Once the **Flume configuration file (`flume-kafka.conf`)** is ready, dont start the Flume agent yet, but this is how you do it:

```bash
flume-ng agent --conf /home/tejasjay94/flume/conf --conf-file /home/tejasjay94/DE_prj/flume-kafka.conf --name agent1 -Dflume.root.logger=INFO,console
```

✅ **Explanation:**

-   `flume-ng agent` → Starts the **Flume agent**.
-   `--conf /home/tejasjay94/flume/conf` → Points to **Flume configuration directory**.
-   `--conf-file /home/tejasjay94/DE_prj/flume-kafka.conf` → Uses the **Flume config file**.
-   `--name agent1` → Runs the **Flume agent named `agent1`**.
-   `-Dflume.root.logger=INFO,console` → **Logs Flume output to the console**.
* * *

## **📌 Step 1.3: Configuring Kafka and MySQL for External Access from Google Colab**

To enable **Google Colab** to access **Kafka and MySQL**, we need to modify their configuration files to:
✅ Allow **external connections** from non-local machines.
✅ Advertise the **public IP address** of the Kafka broker.
✅ Configure MySQL to **listen on all network interfaces** (`0.0.0.0`).

* * *

## **🔹 Step 1: Configuring Kafka for External Access**

### **📌 Modify `server.properties`**

```bash
nano ~/kafka/config/server.properties
```

### **🔍 Breakdown of Kafka Configuration**

```properties
############################# Server Basics #############################
broker.id=0
```

✅ **What It Does:**

-   Assigns a unique **ID (`0`)** to this Kafka broker.
-   If **multiple brokers** exist, each should have a **different ID**.
* * *

```properties
############################# Socket Server Settings #############################
listeners=PLAINTEXT://0.0.0.0:9092,EXTERNAL://0.0.0.0:9093
```

✅ **What It Does:**

-   Kafka listens on **two ports**:
    -   **`9092` (for internal traffic)** → Used by services running inside the GCP VM.
    -   **`9093` (for external traffic)** → Used for clients (e.g., Google Colab).
* * *

```properties
advertised.listeners=PLAINTEXT://localhost:9092,EXTERNAL://35.224.95.121:9093
```

✅ **What It Does:**

-   **Tells external clients (like Google Colab) where to connect.**
-   **`localhost:9092`** → Used by **local applications inside the GCP VM**.
-   **`35.224.95.121:9093`** → Advertises Kafka's **public IP address** for remote clients.

📌 **Replace `35.224.95.121` with your actual GCP VM's external IP.**

* * *

```properties
listener.security.protocol.map=PLAINTEXT:PLAINTEXT,EXTERNAL:PLAINTEXT
```

✅ **What It Does:**

-   Maps both **internal (`PLAINTEXT`) and external (`EXTERNAL`) connections** to **plaintext communication** (no SSL/TLS encryption).
* * *

### **🔹 Restart Kafka to Apply Changes**

```bash
~/kafka/bin/kafka-server-stop.sh
~/kafka/bin/kafka-server-start.sh -daemon ~/kafka/config/server.properties
```

✅ **This stops and restarts the Kafka broker with the updated settings.**

* * *

## **🔹 Step 2: Configuring MySQL for External Access**

### **📌 Modify MySQL Configuration (`mysqld.cnf`)**

```bash
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
```

### **🔍 Breakdown of MySQL Configuration**

```properties
[mysqld]
user = mysql
```

✅ **What It Does:**

-   Runs MySQL as the **`mysql` user**.
* * *

```properties
bind-address            = 0.0.0.0
mysqlx-bind-address     = 0.0.0.0
```

✅ **What It Does:**

-   **`bind-address = 0.0.0.0`** → Allows MySQL to **accept connections from any IP**.
-   **Default MySQL only listens on `127.0.0.1`**, blocking external connections.
-   This change enables **Google Colab** (or any external machine) to access MySQL.
* * *

### **🔹 Restart MySQL to Apply Changes**

```bash
sudo systemctl restart mysql
```

✅ **Ensures MySQL applies the new settings.**

* * *

## **🔍 Step 3: Verify External Connectivity from Google Colab**

### **1️⃣ Test Kafka Connection from Colab**

Run this Python script in Google Colab to check **Kafka connectivity**:

```python
from kafka import KafkaProducer

KAFKA_BROKER = "35.224.95.121:9093"  # Replace with your actual Kafka external IP

try:
    producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)
    print("✅ Successfully connected to Kafka!")
except Exception as e:
    print(f"🚨 Failed to connect: {e}")
```

✅ **Expected Output:**

```
✅ Successfully connected to Kafka!
```

🚨 **If connection fails:**

-   **Ensure port `9093` is open in GCP Firewall.**
-   Run:

    ```bash
    sudo netstat -tulnp | grep 9093
    ```

    If `9093` is not listening, check Kafka logs:

    ```bash
    cat ~/kafka/logs/server.log | tail -n 50
    ```

* * *

### **2️⃣ Test MySQL Connection from Colab**

Run this Python script in Google Colab to check **MySQL connectivity**:

```python
import mysql.connector

try:
    conn = mysql.connector.connect(
        host="35.224.95.121",  # Replace with your MySQL external IP
        user="root",
        password="YOUR_PASSWORD",
        database="iot",
        port=3306
    )
    print("✅ Successfully connected to MySQL!")
except mysql.connector.Error as err:
    print(f"🚨 Failed to connect: {err}")
```

✅ **Expected Output:**

```
✅ Successfully connected to MySQL!
```

🚨 **If connection fails:**

-   Ensure MySQL user **`root` is allowed to connect externally**:

    ```sql
    GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'YOUR_PASSWORD';
    FLUSH PRIVILEGES;
    ```

-   Check if MySQL is **listening on `0.0.0.0:3306`**:

    ```bash
    sudo netstat -tulnp | grep 3306
    ```

-   Restart MySQL:

    ```bash
    sudo systemctl restart mysql
    ```

* * *

## **📌 Step 1.4: Consuming Kafka Logs in Google Colab**

Now that Kafka is **streaming real-time logs**, we need to **consume these logs in Google Colab** and display them.

🔹 **What This Step Does:**

-   **Installs Kafka Client (`kafka-python`)** in Colab.
-   **Retrieves Kafka broker IP** from Colab’s **`userdata` secrets**.
-   **Connects to Kafka topics (`webserver-logs`, `app-logs`, `security-logs`)**.
-   **Prints messages in real time** as logs arrive in Kafka.
* * *

## **🔹 Step 1: Install Required Libraries**

Before using Kafka in **Google Colab**, we need to install the Kafka Python client.

```python
!pip install kafka-python==2.0.2
!pip show kafka-python
```

✅ **What It Does:**

-   Installs `kafka-python` (**version 2.0.2**) to communicate with Kafka.
-   **Verifies installation** using `pip show kafka-python`.
* * *

## **🔹 Step 2: Load Kafka Credentials in Google Colab**

```python
from google.colab import userdata

# Load Kafka broker host from Colab secrets
KAFKA_HOST = userdata.get("KAFKA_HOST")
```

✅ **What It Does:**

-   **Retrieves the Kafka broker’s public IP** from **Colab's secret storage** (`userdata`).
-   Ensures the **IP isn’t hardcoded** in the notebook (**better security**).
* * *

## **🔹 Step 3: Consume Logs from Kafka Topics**

Each Kafka topic corresponds to a different log type: 1️⃣ **Web Server Logs → `webserver-logs`**
2️⃣ **Application Logs → `app-logs`**
3️⃣ **Security Logs → `security-logs`**

Each notebook (`webserver_logs.ipynb`, `app_logs.ipynb`, `IOT_Sensor_data.ipynb`) contains a **Kafka Consumer** for one topic.

* * *

### **1️⃣ Web Server Logs Consumer**

```python
from kafka import KafkaConsumer

# Kafka broker IP (Replace with your Kafka server address)
KAFKA_BROKER = f"{KAFKA_HOST}:9093"

# Connect to Kafka Consumer
consumer = KafkaConsumer(
   "webserver-logs",
   bootstrap_servers=KAFKA_BROKER,
   auto_offset_reset="earliest",
   value_deserializer=lambda m: m.decode("utf-8")
)

print("Listening for Web Server Logs...")

# Read messages from Kafka
for message in consumer:
   print(f"Received: {message.value}")
```

✅ **What It Does:**

-   Connects to **Kafka Broker on port `9093`**.
-   Subscribes to **Kafka topic `webserver-logs`**.
-   Reads logs **from the beginning** (`auto_offset_reset="earliest"`).
-   **Prints received logs in real-time**.
* * *

### **2️⃣ Application Logs Consumer**

```python
from kafka import KafkaConsumer

# Kafka broker IP (Replace with your Kafka server address)
KAFKA_BROKER = f"{KAFKA_HOST}:9093"

# Connect to Kafka Consumer
consumer = KafkaConsumer(
   "app-logs",
   bootstrap_servers=KAFKA_BROKER,
   auto_offset_reset="earliest",
   value_deserializer=lambda m: m.decode("utf-8")
)

print("Listening for Application Logs...")

# Read messages from Kafka
for message in consumer:
   print(f"Received: {message.value}")
```

✅ **What It Does:**

-   Connects to Kafka and listens to **`app-logs` topic**.
-   Prints log messages as they arrive.
* * *

### **3️⃣ Security Logs Consumer**

```python
from kafka import KafkaConsumer

# Kafka broker IP (Replace with your Kafka server address)
KAFKA_BROKER = f"{KAFKA_HOST}:9093"

# Connect to Kafka Consumer
consumer = KafkaConsumer(
   "security-logs",
   bootstrap_servers=KAFKA_BROKER,
   auto_offset_reset="earliest",
   value_deserializer=lambda m: m.decode("utf-8")
)

print("Listening for Security Logs...")

# Read messages from Kafka
for message in consumer:
   print(f"Received: {message.value}")
```

✅ **What It Does:**

-   Connects to Kafka and listens to **`security-logs` topic**.
-   Displays **real-time security events**.
* * *

## **🔍 Step 4: Run Consumers in Google Colab**

### **1️⃣ Open Three Colab Notebooks**

-   `webserver_logs.ipynb` → Run **Web Server Logs consumer**.
-   `app_logs.ipynb` → Run **Application Logs consumer**.
-   `IOT_Sensor_data.ipynb` → Run **Security Logs consumer**.
* * *

### **2️⃣ Expected Output**

When logs arrive in Kafka, Google Colab should print real-time messages:

#### **✅ Web Server Logs**

```
Received: 3f2a1d8e 192.168.1.23 - - [14/Mar/2025:14:30:21 +0000] "GET /index.html HTTP/1.1" 200 2312
```

#### **✅ Application Logs**

```
Received: 3f2a1d8e [2025-03-14 15:20:30] INFO - User logged in
```

#### **✅ Security Logs**

```
Received: 3f2a1d8e [2025-03-14 15:25:12] SECURITY - Unauthorized login attempt
```

* * *

## **📌 Step 2.1: Simulating Real-Time IoT Sensor Data Using Kafka Producer**

Now, we simulate **real-time IoT sensor data** using a **Kafka producer** and send it to **Kafka topic: `iot-sensors`**.

* * *

## **🔍 Understanding `kafka_producer_.py`**

This Python script: ✅ **Generates random IoT sensor readings**.
✅ **Formats data as JSON** for structured storage.
✅ **Sends the data to Kafka topic: `iot-sensors`** every **2 seconds**.

* * *

## **🔹 Step 1: Kafka Producer Setup**

```python
import json
import time
import random
from kafka import KafkaProducer
```

✅ **Imports required libraries:**

-   `json` → Converts Python dict to JSON before sending.
-   `time` → Controls **data generation frequency**.
-   `random` → Generates **random sensor values**.
-   `KafkaProducer` → Connects to Kafka to **send sensor data**.
* * *

## **🔹 Step 2: Initialize Kafka Producer**

```python
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda x: json.dumps(x).encode('utf-8')  # Convert dict to JSON
)
```

✅ **What It Does:**

-   **`bootstrap_servers='localhost:9092'`** → Connects to Kafka running on `localhost` (inside GCP VM).
-   **`value_serializer=lambda x: json.dumps(x).encode('utf-8')`**
    -   Converts Python **dictionary to JSON** (`json.dumps(x)`).
    -   **Encodes as UTF-8** before sending to Kafka.
* * *

## **🔹 Step 3: Define IoT Sensor Data Parameters**

```python
sensor_ids = ["sensor-01", "sensor-02", "sensor-03", "sensor-04", "sensor-05"]
locations = ["Room A", "Room B", "Warehouse", "Factory Floor", "Outdoor"]
sensor_types = ["Temperature", "Pressure", "Humidity", "Proximity", "Motion"]
device_status = ["active", "inactive", "maintenance", "offline"]
```

✅ **What It Does:**

-   **Defines five IoT sensors** (`sensor-01` to `sensor-05`).
-   **Randomly assigns locations** (`Warehouse`, `Factory Floor`, etc.).
-   **Includes multiple sensor types** (`Temperature`, `Pressure`, `Humidity`, etc.).
-   **Defines device status options** (`active`, `offline`, etc.).
* * *

## **🔹 Step 4: Generate IoT Sensor Data**

```python
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
```

✅ **What It Does:**

-   **Randomly selects sensor ID** (`sensor-01` to `sensor-05`).
-   **Generates realistic sensor values:**
    -   **Temperature:** `20.0°C - 30.0°C`
    -   **Pressure:** `900 hPa - 1100 hPa`
    -   **Humidity:** `30% - 60%`
    -   **Battery Level:** `0% - 100%`
-   **Adds a timestamp** for real-time tracking.

✅ **Example Output:**

```json
{
    "sensor_id": "sensor-02",
    "temperature": 25.84,
    "pressure": 980.12,
    "humidity": 48.67,
    "battery_level": 79.34,
    "location": "Warehouse",
    "sensor_type": "Temperature",
    "device_status": "active",
    "timestamp": 1742071031.47151
}
```

* * *

## **🔹 Step 5: Send IoT Data to Kafka**

```python
    producer.send("iot-sensors", data)
    #print(f"Sent: {data}")
    #time.sleep(2)  # Send data every 2 seconds
```

✅ **What It Does:**

-   **Sends JSON data** to Kafka **topic: `iot-sensors`**.
-   **Commented out print statement** (`#print(f"Sent: {data}")`) to avoid excessive logging.
-   **Data is generated continuously** without delay (`time.sleep(2)` is commented out).

📌 **If needed, uncomment `time.sleep(2)` to send data every 2 seconds.**

* * *

## **🔍 Step 6: Running the Kafka Producer**

### **1️⃣ Run Kafka Producer on GCP VM**

```bash
python3 kafka_producer_.py
```

✅ **Expected Output (if print is enabled)**

```
Sent: {"sensor_id": "sensor-03", "temperature": 26.17, "pressure": 1001.32, "humidity": 52.45, "battery_level": 67.80, "location": "Factory Floor", "sensor_type": "Motion", "device_status": "active", "timestamp": 1742071055.9021}
```

* * *

## **📌 Step 2.2: Consuming IoT Sensor Data in Google Colab & Writing to MySQL in Real-Time**

Now, we will: ✅ **Consume IoT sensor data from Kafka in Google Colab**.
✅ **Write the streaming data to a MySQL table running on GCP**.
✅ **Ensure the process runs securely and continuously**.

* * *

## **🔹 Step 1: Install Required Libraries in Google Colab**

```python
!pip install kafka-python==2.0.2
!pip show kafka-python
!pip install mysql-connector-python
```

✅ **What It Does:**

-   Installs **Kafka client (`kafka-python`)** for consuming messages.
-   Installs **MySQL connector** for writing data to MySQL.
-   Verifies the installed version using `pip show kafka-python`.
* * *

## **🔹 Step 2: Load Kafka & MySQL Credentials from Google Colab Secrets**

```python
import mysql.connector
from google.colab import userdata

# Load credentials from Colab's secret storage
KAFKA_HOST = userdata.get("KAFKA_HOST")  # Kafka Broker IP
MYSQL_HOST = userdata.get("MYSQL_HOST")  # MySQL Server IP
MYSQL_USER = userdata.get("MYSQL_USER")  # MySQL Username
MYSQL_PASS = userdata.get("MYSQL_PASS")  # MySQL Password
```

✅ **What It Does:**

-   **Retrieves Kafka and MySQL credentials securely** from Google Colab’s `userdata` storage.
-   **No hardcoded credentials** in the notebook (**better security**).

📌 **Ensure you have set these credentials in Colab:**

```python
userdata.set("KAFKA_HOST", "35.224.95.121")  # Replace with your Kafka external IP
userdata.set("MYSQL_HOST", "35.224.95.121")  # Replace with your MySQL external IP
userdata.set("MYSQL_USER", "root")
userdata.set("MYSQL_PASS", "your_mysql_password")
```

* * *

## **🔹 Step 3: Connect to MySQL & Create Database/Table**

```python
# Connect to MySQL database
conn = mysql.connector.connect(
   host=MYSQL_HOST,
   user=MYSQL_USER,
   password=MYSQL_PASS,
   database="iot"
)

cursor = conn.cursor()
print("✅ Connected to MySQL!")
```

✅ **What It Does:**

-   Establishes **a secure connection to MySQL** using the provided credentials.
-   Selects the **`iot` database** (where we store IoT sensor data).
* * *

### **🔍 Step 3.1: Create Database & Table (if not exists)**

```python
# Create database if it doesn't exist
cursor.execute("CREATE DATABASE IF NOT EXISTS iot")
cursor.execute("USE iot")

# Create table to store IoT sensor data
cursor.execute("""
   CREATE TABLE IF NOT EXISTS sensor_data (
       id INT AUTO_INCREMENT PRIMARY KEY,
       sensor_id VARCHAR(50),
       temperature FLOAT,
       pressure FLOAT,
       humidity FLOAT,
       battery_level FLOAT,
       location VARCHAR(100),
       sensor_type VARCHAR(50),
       device_status VARCHAR(50),
       timestamp DOUBLE
   )
""")

print("✅ Database and table created successfully!")
```

✅ **What It Does:**

-   **Ensures database `iot` exists**.
-   **Creates `sensor_data` table** (if not already created).

📌 **Columns Explanation:**

| Column | Data Type | Description |
| --- | --- | --- |
| `id` | `INT` (Primary Key) | Auto-incremented unique ID |
| `sensor_id` | `VARCHAR(50)` | Unique sensor identifier |
| `temperature` | `FLOAT` | Temperature in Celsius |
| `pressure` | `FLOAT` | Pressure in hPa |
| `humidity` | `FLOAT` | Humidity percentage |
| `battery_level` | `FLOAT` | Sensor battery level |
| `location` | `VARCHAR(100)` | Location of the sensor |
| `sensor_type` | `VARCHAR(50)` | Type of sensor (Temperature, Pressure, etc.) |
| `device_status` | `VARCHAR(50)` | Sensor status (Active, Offline, etc.) |
| `timestamp` | `DOUBLE` | Unix timestamp of event |

* * *

## **🔹 Step 4: Consume Kafka Messages & Store in MySQL**

```python
import json
from kafka import KafkaConsumer

# Define Kafka broker address
KAFKA_BROKER = f"{KAFKA_HOST}:9093"

# Initialize Kafka Consumer
consumer = KafkaConsumer(
   "iot-sensors",
   bootstrap_servers=KAFKA_BROKER,
   auto_offset_reset='earliest',
   value_deserializer=lambda x: json.loads(x.decode('utf-8'))  # Convert JSON to dict
)

print("✅ Listening for IoT Sensor Data...")

# Process Kafka messages
for message in consumer:
   data = message.value
   print(f"Received: {data}")

   # Insert Data into MySQL
   sql = """
   INSERT INTO sensor_data (sensor_id, temperature, pressure, humidity, battery_level, location, sensor_type, device_status, timestamp)
   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
   """
   values = (
       data["sensor_id"],
       data["temperature"],
       data["pressure"],
       data["humidity"],
       data["battery_level"],
       data["location"],
       data["sensor_type"],
       data["device_status"],
       data["timestamp"],
   )

   cursor.execute(sql, values)
   conn.commit()

   print("✅ Data successfully stored in MySQL!")
```

✅ **What It Does:**

-   Connects to **Kafka topic: `iot-sensors`**.
-   Reads **real-time IoT sensor messages** from Kafka.
-   Parses **JSON messages** and extracts sensor details.
-   **Inserts data into MySQL table (`sensor_data`)**.
-   **Commits transactions continuously** so no data is lost.

📌 **Example Output (Google Colab)**

```
✅ Listening for IoT Sensor Data...
Received: {'sensor_id': 'sensor-03', 'temperature': 26.17, 'pressure': 1001.32, 'humidity': 52.45, 'battery_level': 67.80, 'location': 'Factory Floor', 'sensor_type': 'Motion', 'device_status': 'active', 'timestamp': 1742071055.9021}
✅ Data successfully stored in MySQL!
```

* * *

## **📌 Step 2.3: Automating the IoT Data Pipeline Using a Shell Script**

Now, we will **automate the entire process** using a shell script (`automate.sh`). This script ensures:
✅ **All services start automatically** if they are not already running.
✅ **Kafka topics are created only if they do not exist**.
✅ **Log generators, Flume, and Kafka Producer start automatically**.

* * *

## **🔹 Step 1: Understanding `automate.sh`**

This script:

-   **Checks if each process is running** before starting it.
-   **Starts Zookeeper & Kafka** (if not running).
-   **Creates Kafka topics** if they don’t exist.
-   **Starts log generators, Flume, and Kafka Producer**.
* * *

## **🔍 Breakdown of the Script**

### **1️⃣ Function to Check Running Processes**

```bash
# Function to check if a process is running
is_running() {
    pgrep -f "$1" > /dev/null 2>&1
}
```

✅ **What It Does:**

-   Uses **`pgrep -f`** to **check if a process is running**.
-   **Returns `true` if the process is found**, otherwise `false`.
-   **Redirects errors to `/dev/null`** (`2>&1`) to suppress unwanted messages.
* * *

### **2️⃣ Start Zookeeper (If Not Running)**

```bash
if is_running "QuorumPeerMain"; then
    echo "Zookeeper is already running."
else
    echo "Starting Zookeeper..."
    ~/kafka/bin/zookeeper-server-start.sh ~/kafka/config/zookeeper.properties &
    sleep 20
fi
```

✅ **What It Does:**

-   Checks if **Zookeeper (`QuorumPeerMain`) is running**.
-   If not, **starts Zookeeper in the background** (`&`) and **waits for 20 seconds**.
* * *

### **3️⃣ Start Kafka Broker (If Not Running)**

```bash
if is_running "kafka.Kafka"; then
    echo "Kafka Broker is already running."
else
    echo "Starting Kafka Broker..."
    ~/kafka/bin/kafka-server-start.sh ~/kafka/config/server.properties &
    sleep 20
fi
```

✅ **What It Does:**

-   Checks if **Kafka broker (`kafka.Kafka`) is running**.
-   If not, **starts Kafka broker in the background** and **waits 20 seconds**.
* * *

### **4️⃣ Create Kafka Topics (Only If Not Already Created)**

```bash
echo "Ensuring Kafka topics exist..."
~/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092 | grep -q "webserver-logs" || \
~/kafka/bin/kafka-topics.sh --create --topic webserver-logs --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

~/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092 | grep -q "app-logs" || \
~/kafka/bin/kafka-topics.sh --create --topic app-logs --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

~/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092 | grep -q "security-logs" || \
~/kafka/bin/kafka-topics.sh --create --topic security-logs --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

✅ **What It Does:**

-   Lists existing Kafka topics using **`kafka-topics.sh --list`**.
-   **Checks if each topic exists** (`grep -q "topic-name"`).
-   **Creates the topic only if it does not exist** (`||` executes if `grep` fails).

📌 **Topics Created:**

-   `webserver-logs`
-   `app-logs`
-   `security-logs`
* * *

### **5️⃣ Start Log Generators (If Not Running)**

```bash
for script in "generate_logs.py" "generate_app_logs.py" "generate_security_logs.py"; do
    if is_running "$script"; then
        echo "$script is already running."
    else
        echo "Starting $script..."
        python3 ~/DE_prj/$script &
    fi
done
```

✅ **What It Does:**

-   Loops through **all log generation scripts**.
-   **Checks if each script is running** before starting it.
-   **Runs each script in the background (`&`)** if it’s not already running.
* * *

### **6️⃣ Start Flume (If Not Running)**

```bash
if is_running "flume-ng"; then
    echo "Flume is already running."
else
    echo "Starting Flume..."
    flume-ng agent --conf ~/DE_prj/conf --conf-file ~/DE_prj/flume-kafka.conf --name agent1 -Dflume.root.logger=INFO,console &
fi
```

✅ **What It Does:**

-   Checks if **Flume is running**.
-   If not, **starts Flume agent** to stream logs into Kafka.
* * *

### **7️⃣ Start Kafka Producer (If Not Running)**

```bash
if is_running "kafka_producer_.py"; then
    echo "Kafka producer is already running."
else
    echo "Starting Kafka producer..."
    python3 ~/DE_prj/kafka_producer_.py &
fi
```

✅ **What It Does:**

-   Checks if the **Kafka producer script is running**.
-   If not, **starts it in the background (`&`)** to send IoT sensor data to Kafka.
* * *

### **8️⃣ Display Final Message**

```bash
echo "All required services are running!"
```

✅ **What It Does:**

-   **Confirms that all services are up and running.**
* * *

## **🔹 Step 2: Running the Automation Script**

1️⃣ **Make the script executable**:

```bash
chmod +x ~/DE_prj/automate.sh
```

2️⃣ **Run the script**:

```bash
~/DE_prj/automate.sh
```

✅ **Expected Output:**

```
Zookeeper is already running.
Kafka Broker is already running.
Ensuring Kafka topics exist...
webserver-logs topic exists.
app-logs topic exists.
security-logs topic exists.
generate_logs.py is already running.
generate_app_logs.py is already running.
generate_security_logs.py is already running.
Flume is already running.
Kafka producer is already running.
All required services are running!
```

🚀 **Now everything is running automatically!**

* * *

## **📌 Step 2.4: Verify IoT Sensor Data in MySQL on GCP VM**

Now that **IoT sensor data is being written to MySQL**, we need to verify that the **data exists in the MySQL database** on the **Google Cloud VM**.

* * *

## **🔹 Step 1: Log into MySQL on GCP VM**

Run the following command in the **Google Cloud VM terminal**:

```bash
mysql -u TejasJay -p
```

✅ **What It Does:**

-   Connects to **MySQL as user `TejasJay`**.
-   **Prompts for the password** (`-p`).

📌 **Replace `TejasJay` with your MySQL username if different.**

* * *

## **🔹 Step 2: Switch to the `iot` Database**

```sql
USE iot;
```

✅ **What It Does:**

-   **Selects the `iot` database** where sensor data is stored.
* * *

## **🔹 Step 3: Query the `sensor_data` Table**

```sql
SELECT * FROM sensor_data LIMIT 5;
```

✅ **What It Does:**

-   Retrieves **the first 5 records** from **`sensor_data`** to verify data ingestion.

✅ **Expected Output:**

```
+----+-----------+-------------+----------+----------+---------------+---------------+-------------+---------------+--------------------+
| id | sensor_id | temperature | pressure | humidity | battery_level | location      | sensor_type | device_status | timestamp          |
+----+-----------+-------------+----------+----------+---------------+---------------+-------------+---------------+--------------------+
|  1 | sensor-01 |       27.89 |   962.88 |    56.02 |         37.73 | Outdoor       | Proximity   | inactive      | 1742090006.7988386 |
|  2 | sensor-04 |       25.45 |   984.37 |     38.4 |         74.74 | Factory Floor | Temperature | active        | 1742090007.0364344 |
|  3 | sensor-02 |       24.25 |   1065.5 |    43.97 |         52.47 | Factory Floor | Motion      | offline       | 1742090007.0365453 |
|  4 | sensor-02 |       26.34 |  1003.29 |    45.75 |         76.36 | Outdoor       | Humidity    | inactive      | 1742090007.0366478 |
|  5 | sensor-03 |        28.3 |  1074.76 |    58.67 |         38.74 | Room A        | Pressure    | maintenance   |  1742090007.036723 |
+----+-----------+-------------+----------+----------+---------------+---------------+-------------+---------------+--------------------+
```

✅ **Confirms that:**

-   **Data is successfully stored** in MySQL.
-   **Timestamps are being recorded correctly**.

📌 **If no data is found, check Kafka Consumer logs to ensure it is inserting records.**

* * *

## **📌 Step 2.5: Connect MySQL to Google Looker Studio for Real-Time Analytics**

🔹 Now, we will **connect MySQL to Google Looker Studio** and create **a real-time dashboard**.

* * *

### **🔹 Step 1: Enable Public Access for MySQL (if not already)**

To allow Looker Studio to access MySQL: 1️⃣ **Open Google Cloud Console** → Navigate to **SQL > Instances**.
2️⃣ Click on your **MySQL instance**.
3️⃣ Under **"Connections"**, ensure that **"Public IP Address"** is enabled.
4️⃣ Add **Looker Studio’s IP range (`0.0.0.0/0`)** in the **"Authorized Networks"** section.

* * *

### **🔹 Step 2: Grant Looker Studio Access to MySQL**

Run the following command in **Google Cloud VM’s MySQL**:

```sql
GRANT ALL PRIVILEGES ON iot.* TO 'TejasJay'@'%' IDENTIFIED BY 'your_mysql_password';
FLUSH PRIVILEGES;
```

✅ **What It Does:**

-   Allows **external connections** from **Looker Studio**.
-   Grants full access to **database `iot`** for the user **`TejasJay`**.
-   **Replaces `'your_mysql_password'`** with your **actual MySQL password**.

📌 **Now, MySQL is accessible externally, including by Looker Studio.**

* * *

### **🔹 Step 3: Connect MySQL to Looker Studio**

1️⃣ **Go to Looker Studio**:
🔗 [https://lookerstudio.google.com](https://lookerstudio.google.com/)

2️⃣ **Click on "Create" → "Data Source"**.

3️⃣ **Select "MySQL" as the data source**.

4️⃣ **Enter Database Credentials**:

-   **Host**: _(Your GCP MySQL External IP)_
-   **Port**: `3306`
-   **Database**: `iot`
-   **Username**: `TejasJay`
-   **Password**: _(Your MySQL Password)_

5️⃣ **Click "Authenticate" and "Connect"**.

* * *

### **🔹 Step 4: Create Real-Time Dashboards**

Once connected, you can: ✅ **Visualize sensor data in charts and tables**.
✅ **Create filters for different sensor types** (`Temperature`, `Humidity`, `Pressure`, etc.).
✅ **Plot real-time sensor trends (Temperature over Time, Humidity over Time, etc.)**.
✅ **Monitor device status (`active`, `inactive`, `maintenance`)**.

📌 **Example Looker Studio Dashboard:**

-   **Line Chart**: `Temperature` vs. `Time`
-   **Bar Chart**: `Average Humidity by Location`
-   **Table**: `Live IoT Sensor Readings`
* * *



