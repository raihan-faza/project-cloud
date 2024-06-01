import docker
import datetime
import threading

# Initialize the Docker client
client = docker.from_env()

# Function to log events
def log_event(event):
    event_time = datetime.datetime.fromtimestamp(event['time'])
    event_date = event_time.strftime('%Y-%m-%d')
    event_time = event_time.strftime('%H:%M:%S')
    event_action = event['Action']
    event_container_name = event['Actor']['Attributes'].get('name', 'unknown')
    event_container_id = event['Actor']['ID']
    log_message = f"{event_date};{event_time};{event_container_name};{event_container_id};{event_action}"
    print(log_message)
    with open("docker_events.log", "a") as log_file:
        log_file.write(log_message + "\n")

# Check the existing log file content (optional, for debugging purposes)
def check_log_file():
    try:
        with open("docker_events.log", "r") as log_file:
            content = log_file.read()
            print("Existing log file content:\n" + content)
    except FileNotFoundError:
        print("Log file does not exist yet.")

# Uncomment the following line to check the log file content at the start
# check_log_file()

# Function to listen for Docker events
def listen_to_events():
    for event in client.events(decode=True):
        if event['Type'] == 'container' and event['Action'] in ['create', 'start', 'pause', 'unpause', 'stop', 'destroy', 'die']:
            log_event(event)

# Listen for Docker events
# for event in client.events(decode=True):
#     if event['Type'] == 'container' and event['Action'] in ['create', 'start', 'pause', 'unpause', 'stop', 'destroy', 'die']:
#         log_event(event)

# Start the event listener in a separate thread
# event_listener_thread = threading.Thread(target=listen_to_events, daemon=True)
# event_listener_thread.start()

