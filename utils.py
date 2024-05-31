import subprocess
import docker

def get_docker_containers():
    try:
        # Run the 'docker ps' command to get the list of running containers
        result = subprocess.run(['docker', 'ps', '--format', '{{.ID}} {{.Names}}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Error running docker command: {result.stderr}")
        
        containers = result.stdout.strip().split('\n')
        container_info = [line.split() for line in containers if line]
        
        return [{'ID': info[0], 'Name': info[1]} for info in container_info]
    
    except Exception as e:
        return str(e)

def get_container_stats(container_id):
    client = docker.from_env()
    try:
        container = client.containers.get(container_id)
        stats = container.stats(stream=False)
        return stats
    except docker.errors.NotFound:
        return f"Container with ID {container_id} not found."
    except docker.errors.APIError as e:
        return f"Error communicating with Docker API: {e}"
    finally:
        client.close()

# Example usage
# containers = get_docker_containers()
# for container in containers:
#     print(f"ID: {container['ID']}, Name: {container['Name']}")

client=docker.from_env()
container = client.containers.get('a6f44e5db3b1')
stats = container.stats(stream=False)
# stats = container.stats(stream=False)
# print(stats.keys())
print(stats['storage_stats'])
print(stats['cpu_stats'])
print(stats['memory_stats'])
