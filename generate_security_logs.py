import time
import random
import uuid

security_events = [
    "Unauthorized login attempt",
    "Firewall rule updated",
    "SSH access granted",
    "Intrusion detected",
    "User account locked due to failed login attempts",
    "Security patch applied",
    "Malware scan completed"
]

log_format = '{session_id} [{timestamp}] SECURITY - {event}'

# Generate a session ID that remains stable for a period
session_id = str(uuid.uuid4())[:8]
start_time = time.time()

with open("security_logs.txt", "a") as log_file:
    while True:
        if time.time() - start_time > 300:  # 5 minutes
            session_id = str(uuid.uuid4())[:8]
            start_time = time.time()

        log_entry = log_format.format(
            session_id=session_id,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            event=random.choice(security_events)
        )
        log_file.write(log_entry + "\n")
        # print(f"Generated Security Log: {log_entry}")
        log_file.flush()
        time.sleep(3)
