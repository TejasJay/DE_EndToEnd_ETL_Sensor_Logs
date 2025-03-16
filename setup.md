
# **📌 IoT Sensor Data Streaming & Analytics Setup Guide**  

This guide provides **step-by-step instructions** to set up a real-time **IoT sensor data pipeline** using:  
✅ **Kafka** (Event Streaming)  
✅ **Flume** (Log Streaming)  
✅ **MySQL** (Database Storage)  
✅ **Google Colab** (Kafka Consumer)  
✅ **Google Cloud Platform (GCP)**  
✅ **Looker Studio** (Real-time Analytics)  

---

## **📌 Step 1: Setting Up the Environment on Google Cloud**
We will set up a **Google Cloud Virtual Machine (VM)** to run **Kafka, Flume, and MySQL**.

### **🔹 Step 1.1: Create a GCP VM Instance**
1️⃣ Go to **Google Cloud Console** → Compute Engine → VM Instances  
2️⃣ Click **"Create Instance"**  
3️⃣ **Choose configuration:**
   - **Machine type:** `e2-standard-2` (2 vCPUs, 8GB RAM)  
   - **OS:** `Ubuntu 22.04 LTS`  
   - **Boot disk size:** `50GB`  
   - **Firewall:** Check ✅ **Allow HTTP & HTTPS**  
4️⃣ **Click "Create"**

### **🔹 Step 1.2: Set Up SSH Access**
1️⃣ Open **Google Cloud Shell**  
2️⃣ Connect to your VM:  
   ```bash
   gcloud compute ssh your-vm-name --zone=your-zone
   ```
3️⃣ Update system packages:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

---

## **📌 Step 2: Install Required Tools**
### **🔹 Step 2.1: Install Java (Required for Kafka & Flume)**
```bash
sudo apt install openjdk-11-jdk -y
java -version
```

### **🔹 Step 2.2: Install Kafka**
```bash
wget https://downloads.apache.org/kafka/3.2.3/kafka_2.13-3.2.3.tgz
tar -xvf kafka_2.13-3.2.3.tgz
mv kafka_2.13-3.2.3 ~/kafka
```

**Start Kafka:**
```bash
~/kafka/bin/zookeeper-server-start.sh ~/kafka/config/zookeeper.properties &
~/kafka/bin/kafka-server-start.sh ~/kafka/config/server.properties &
```

---

### **🔹 Step 2.3: Install Apache Flume**
```bash
wget https://downloads.apache.org/flume/1.10.1/apache-flume-1.10.1-bin.tar.gz
tar -xvf apache-flume-1.10.1-bin.tar.gz
mv apache-flume-1.10.1-bin ~/flume
```

---

### **🔹 Step 2.4: Install MySQL**
```bash
sudo apt install mysql-server -y
sudo systemctl start mysql
sudo systemctl enable mysql
```

**Create MySQL user & database:**
```sql
CREATE DATABASE iot;
CREATE USER 'TejasJay'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON iot.* TO 'TejasJay'@'%';
FLUSH PRIVILEGES;
```

Enable **external MySQL access**:
```bash
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
```
Change:
```ini
bind-address = 0.0.0.0
```
Restart MySQL:
```bash
sudo systemctl restart mysql
```

---

## **📌 Step 3: Configure Kafka, Flume & MySQL**
### **🔹 Step 3.1: Configure Kafka for External Access**
Modify `server.properties`:
```bash
nano ~/kafka/config/server.properties
```
Change:
```properties
listeners=PLAINTEXT://0.0.0.0:9092,EXTERNAL://0.0.0.0:9093
advertised.listeners=PLAINTEXT://localhost:9092,EXTERNAL://your-external-ip:9093
listener.security.protocol.map=PLAINTEXT:PLAINTEXT,EXTERNAL:PLAINTEXT
```
Restart Kafka:
```bash
~/kafka/bin/kafka-server-stop.sh
~/kafka/bin/kafka-server-start.sh -daemon ~/kafka/config/server.properties
```

---

### **🔹 Step 3.2: Configure Flume to Stream Logs**
Modify `flume-kafka.conf`:
```properties
agent1.sources.source1.command = tail -F ~/DE_prj/webserver_logs.txt
agent1.sinks.sink1.kafka.topic = webserver-logs
```
Start Flume:
```bash
flume-ng agent --conf ~/flume/conf --conf-file ~/DE_prj/flume-kafka.conf --name agent1 -Dflume.root.logger=INFO,console &
```

---

## **📌 Step 4: Automate Everything Using a Shell Script**
Create `automate.sh`:
```bash
nano ~/DE_prj/automate.sh
```
Paste:
```bash
#!/bin/bash
~/kafka/bin/zookeeper-server-start.sh ~/kafka/config/zookeeper.properties &
sleep 10
~/kafka/bin/kafka-server-start.sh ~/kafka/config/server.properties &
sleep 10
python3 ~/DE_prj/kafka_producer_.py &
python3 ~/DE_prj/generate_logs.py &
flume-ng agent --conf ~/DE_prj/conf --conf-file ~/DE_prj/flume-kafka.conf --name agent1 &
```
Make it executable:
```bash
chmod +x ~/DE_prj/automate.sh
```
Run the script:
```bash
~/DE_prj/automate.sh
```

---

## **📌 Step 5: Set Up Google Colab for Kafka & MySQL**
### **🔹 Step 5.1: Install Dependencies in Colab**
```python
!pip install kafka-python mysql-connector-python
```

### **🔹 Step 5.2: Connect to Kafka**
```python
from kafka import KafkaConsumer
consumer = KafkaConsumer(
   "iot-sensors",
   bootstrap_servers="your-external-ip:9093",
   value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)
```

### **🔹 Step 5.3: Connect to MySQL**
```python
import mysql.connector
conn = mysql.connector.connect(
    host="your-external-ip",
    user="TejasJay",
    password="your_password",
    database="iot"
)
cursor = conn.cursor()
cursor.execute("SELECT * FROM sensor_data LIMIT 5;")
print(cursor.fetchall())
```

---

## **📌 Step 6: Connect MySQL to Looker Studio**
1️⃣ Open **[Looker Studio](https://lookerstudio.google.com/)**  
2️⃣ Click **Create → Data Source → MySQL**  
3️⃣ Enter:  
   - **Host**: `your-external-ip`  
   - **Database**: `iot`  
   - **Username**: `TejasJay`  
   - **Password**: `your_password`  
4️⃣ Click **Connect → Create Dashboard**  

🎉 **Now, visualize sensor trends in real-time!**  

---
