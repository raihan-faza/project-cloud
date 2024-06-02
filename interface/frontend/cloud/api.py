# api.py
import requests

BASE_URL = 'http://103.181.182.243:8080/container/'

def delete_container(container_id, access_token):
    try:
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
        response = requests.post(f'{BASE_URL}delete/', json={'ContainerID':container_id}, headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(e)
        return False
    
def start_container(container_id, access_token):
    try:
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
        response = requests.post(f'{BASE_URL}start/', json={'ContainerID':container_id}, headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(e)
        return False

def stop_container(container_id, access_token):
    try:
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
        response = requests.post(f'{BASE_URL}stop/', json={'ContainerID':container_id}, headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(e)
        return False

def pause_container(container_id, access_token):
    try:
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
        response = requests.post(f'{BASE_URL}pause/', json={'ContainerID':container_id}, headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(e)
        return False

def unpause_container(container_id, access_token):
    try:
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
        response = requests.post(f'{BASE_URL}unpause/', json={'ContainerID':container_id}, headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(e)
        return False


def edit_container(container_id, ram, access_token):
    try:
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
        body = {'ContainerID':container_id, 'NewRam':ram}
        response = requests.post(f'{BASE_URL}update/', json=body, headers=headers)
        print(response.json())
        return response.status_code == 200
    except Exception as e:
        print(e)
        return False
        
    