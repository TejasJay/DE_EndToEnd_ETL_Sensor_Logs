import time
import random
import uuid

# Generate a session ID that remains stable for a period
session_id = str(uuid.uuid4())[:8]

log_format = '{session_id} {ip} - - [{timestamp}] "GET /index.html HTTP/1.1" 200 {bytes}'

start_time = time.time()  # Store session start time

with open("webserver_logs.txt", "a") as log_file:
    while True:
        # If 5 minutes have passed, generate a new session ID
        if time.time() - start_time > 300:  # 300 seconds = 5 minutes
            session_id = str(uuid.uuid4())[:8]
            start_time = time.time()  # Reset timer

        log_entry = log_format.format(
            session_id=session_id,
            ip=f"192.168.1.{random.randint(1, 255)}",
            timestamp=time.strftime("%d/%b/%Y:%H:%M:%S +0000"),
            bytes=random.randint(500, 5000)
        )
        log_file.write(log_entry + "\n")
        # print(f"Generated Web Log: {log_entry}")
        log_file.flush()
        time.sleep(2)
