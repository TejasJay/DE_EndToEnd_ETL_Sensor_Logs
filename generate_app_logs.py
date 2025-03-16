import time
import random
import uuid

app_log_levels = ["INFO", "WARN", "ERROR", "DEBUG"]
log_format = '{session_id} [{timestamp}] {log_level} - {message}'

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

# Generate a session ID that remains stable for a period
session_id = str(uuid.uuid4())[:8]
start_time = time.time()

with open("app_logs.txt", "a") as log_file:
    while True:
        if time.time() - start_time > 300:  # 5 minutes
            session_id = str(uuid.uuid4())[:8]
            start_time = time.time()

        log_entry = log_format.format(
            session_id=session_id,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            log_level=random.choice(app_log_levels),
            message=random.choice(messages)
        )
        log_file.write(log_entry + "\n")
        # print(f"Generated App Log: {log_entry}")
        log_file.flush()
        time.sleep(2)
