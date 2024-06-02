# api.py
import requests

BASE_URL = 'http://103.181.182.243:8080/container/'

def delete_container(container_id, access_token):
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
    response = requests.delete(f'{BASE_URL}delete/', json={'container_Id':container_id}, headers=headers)
    return response.status_code == 200

def stop_container(container_id, access_token):
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
    response = requests.delete(f'{BASE_URL}stop/', json={'container_Id':container_id}, headers=headers)
    return response.status_code == 200

def pause_container(container_id, access_token):
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
    response = requests.post(f'{BASE_URL}pause/', json={'container_Id':container_id}, headers=headers)
    return response.status_code == 200

def unpause_container(container_id, access_token):
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
    response = requests.post(f'{BASE_URL}unpause/', json={'container_Id':container_id}, headers=headers)
    return response.status_code == 200