import docker
from datetime import datetime, timedelta
import time

# Constants for billing rates (example rates)
RATE_PER_MINUTE = 100  # Rate per hour of uptime in dollars

# Create a Docker client
client = docker.from_env()

# Function to calculate billing
def calculate_billing(uptime_seconds, rate):
    uptime = uptime_seconds // 60 + 1

    total_cost = uptime * rate

    return total_cost

# Function to monitor and calculate billing for a container
def monitor_container(container_id, uptime, rate):
    try:
        container = client.containers.get(container_id)

        # Calculate billing
        cost = calculate_billing(uptime, rate)

        # Print or log the billing information
        print(f"Container ID: {container.id}")
        print(f"Status: {container.status}")
        print(f"Uptime: {uptime} seconds")
        print(f"Current Billing Cost: Rp.{cost}")

    except docker.errors.NotFound:
        print(f'Container {container_id} not found')
    except docker.errors.APIError as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    # Example usage
    image_name = "nginx"
    container_name = "my_nginx"
    ports = {'80/tcp': 8080}
    
    # Run container
    container = client.containers.run(image_name, name=container_name, ports=ports, detach=True)
    print(f'Container {container.id} started')

    # Start monitoring the container in a separate thread
    import threading
    monitor_thread = threading.Thread(target=monitor_container, args=(container.id, 100, RATE_PER_MINUTE))
    monitor_thread.start()

    # Wait for the monitor thread to finish
    monitor_thread.join()