# api.py
import os
from dotenv import load_dotenv
import requests
import jwt

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
LOG_URL = os.getenv("LOG_URL")
BASE_URL = 'http://103.181.182.243:8080/container/'

def delete_container(container_id, access_token):
    try:
        user = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
        print(user)
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
        response = requests.post(f'{BASE_URL}delete/', json={'ContainerID':container_id}, headers=headers)
        log_entry = {
                    "user_id": user['uuid'],
                    "container_id": container_id,
                    "action": "delete"
                }
        resp = requests.post(f'{LOG_URL}/log/add', json=log_entry, headers=headers)
        log = resp.json()
        print(log)
        return response.status_code == 200
    except Exception as e:
        print(e)
        return False
    
def start_container(container_id, access_token):
    try:
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
        response = requests.post(f'{BASE_URL}start/', json={'ContainerID':container_id}, headers=headers)
        user = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
        log_entry = {
                    "user_id": user['uuid'],
                    "container_id": container_id,
                    "action": "start"
                }
        resp = requests.post(f'{LOG_URL}/log/add', json=log_entry, headers=headers)
        log = resp.json()
        print(log)
        return response.status_code == 200
        
    except Exception as e:
        print(e)
        return False

def stop_container(container_id, access_token):
    try:
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
        response = requests.post(f'{BASE_URL}stop/', json={'ContainerID':container_id}, headers=headers)
        user = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
        log_entry = {
                    "user_id": user['uuid'],
                    "container_id": container_id,
                    "action": "stop"
                }
        resp = requests.post(f'{LOG_URL}/log/add', json=log_entry, headers=headers)
        log = resp.json()
        print(log)
        return response.status_code == 200
    except Exception as e:
        print(e)
        return False

def pause_container(container_id, access_token):
    try:
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
        response = requests.post(f'{BASE_URL}pause/', json={'ContainerID':container_id}, headers=headers)
        user = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
        log_entry = {
                    "user_id": user['uuid'],
                    "container_id": container_id,
                    "action": "pause"
                }
        resp = requests.post(f'{LOG_URL}/log/add', json=log_entry, headers=headers)
        log = resp.json()
        print(log)
        return response.status_code == 200
    except Exception as e:
        print(e)
        return False

def unpause_container(container_id, access_token):
    try:
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
        response = requests.post(f'{BASE_URL}unpause/', json={'ContainerID':container_id}, headers=headers)
        user = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
        log_entry = {
                    "user_id": user['uuid'],
                    "container_id": container_id,
                    "action": "unpause"
                }
        resp = requests.post(f'{LOG_URL}/log/add', json=log_entry, headers=headers)
        log = resp.json()
        print(log)
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
        user = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
        log_entry = {
                    "user_id": user['uuid'],
                    "container_id": container_id,
                    "action": "edit"
                }
        resp = requests.post(f'{LOG_URL}/log/add', json=log_entry, headers=headers)
        log = resp.json()
        print(log)
        return response.status_code == 200
    except Exception as e:
        print(e)
        return False
        
    