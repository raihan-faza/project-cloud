from datetime import datetime
import os
from django.shortcuts import redirect, render
from dotenv import load_dotenv
import requests
from django.contrib import messages
# Create your views here.
load_dotenv()
API_URL = os.getenv("API_URL")
LOG_URL = os.getenv("LOG_URL")

def refresh_token(request):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f'{API_URL}/refresh-token', headers=headers, json={'refresh_token': request.session['refresh_token']})
    if response.status_code != 200:
        return False
    data = response.json()
    if 'access_token' in data:
        request.session['access_token'] = data['access_token']
        request.session['refresh_token'] = data['refresh_token']
        return True
    else:
        return False

def index(request):
    if 'user' in request.session:
        try:
            profile = requests.get(f'{API_URL}/profile', headers={'Authorization': f'Bearer {request.session["access_token"]}'})
            user = profile.json().get('user')
            try:
                container_list = requests.get('http://103.181.182.243:8080/container/list/', headers={'Authorization': f'Bearer {request.session["access_token"]}'})
                print(profile.json())
                data = container_list.json()
                print(data.get("data"))
                return render(request, 'index.html', {'user': user, 'containers': data.get("data")})
            except Exception as e:
                print(e)
                print(user)
                return render(request, 'index.html', {'user': user})
        except Exception as e:
            print(e)
            return render(request, 'index.html', {'user': request.session['user']})
    else:
        if 'refresh_token' in request.session:
            is_refreshed = refresh_token(request)
            if is_refreshed:
                return render(request, 'index.html', {'user': request.session['user']})
            else:
                return redirect('login')
        return redirect('login')
            
    
def login(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            headers = {'Content-Type': 'application/json'}
            response = requests.post(f'{API_URL}/login', headers=headers, json={'email': email, 'password': password})
            data = response.json()
            if 'access_token' in data and 'refresh_token' in data:
                request.session['access_token'] = data['access_token']
                request.session['refresh_token'] = data['refresh_token']
                request.session['user'] = data['user']
                print(request.session['user'])
                return redirect('index')
            else:
                return render(request, 'login.html', {'error': 'Invalid credentials'})
        except Exception as e:
            print(e)
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        headers = {'Content-Type': 'application/json'}
        response = requests.post(f'{API_URL}/register', headers=headers, json={'email': email, 'username': username, 'password': password})
        data = response.json()
        if 'message' in data:
            messages.success(request, data['message'])
            return redirect('login')
    return render(request, 'signup.html')

def recharge(request):
    if request.method == 'POST':
        if 'access_token' not in request.session:
            return redirect('login')
        else:
            gross_amount = request.POST.get('gross_amount')
            headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {request.session["access_token"]}'}
            body = {'gross_amount': gross_amount}
            response = requests.post(f'{API_URL}/payment/charge', headers=headers, json=body)
            data = response.json()
            if 'message' in data:
                print(data)
                return redirect(data['data'].get('redirect_url'))
    return render(request, 'recharge.html')

def logout(request):
    if 'user' in request.session:
        request.session.flush()
        messages.success(request, 'You have been logged out')
        return redirect('login')
    
def create_container(request):
    if request.method == 'POST':
        if 'access_token' not in request.session:
            messages.error(request, 'You must be logged in to create a container')
            return redirect('login')
        else:
            print(request.session['access_token'])
            container_name = request.POST.get('container_name')
            container_password = request.POST.get('container_password')
            ram = int(request.POST.get('ram'))
            core = int(request.POST.get('core'))
            headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {request.session["access_token"]}'}
            body = {"ContainerName": container_name,"ContainerPassword": container_password, "ContainerRam": ram, "ContainerCore": core}
            print(body)
            response = requests.post('http://103.181.182.243:8080/container/create', headers=headers, json=body)
            if response.status_code == 200:
                log_entry = {
                    "user_id": request.session['user']['uuid'],
                    "container_id": response.json().get('container_Id'),
                    "action": "create"
                }
                resp = requests.post(f'{LOG_URL}/log/add', json=log_entry, headers=headers)
                log = resp.json()
                print(log)
                data = response.json()
                if 'container_Id' in data:
                    return redirect('index')
            else:
                print(response.json())
                return redirect('index')
    return redirect('index')

# views.py
from .api import delete_container, edit_container, pause_container, start_container, stop_container, unpause_container

def delete_container_view(request):
    container_id = request.POST.get('container_id')    
    if 'access_token' not in request.session:
        messages.error(request, 'You must be logged in to delete a container')
        return redirect('login')
    else:
        success = delete_container(container_id, request.session['access_token'])
        return redirect('index')

def stop_container_view(request):
    container_id = request.POST.get('container_id')    
    if 'access_token' not in request.session:
        messages.error(request, 'You must be logged in to delete a container')
        return redirect('login')
    else:
        success = stop_container(container_id, request.session['access_token'])
        return redirect('index')
    
def pause_container_view(request):
    container_id = request.POST.get('container_id')    
    if 'access_token' not in request.session:
        messages.error(request, 'You must be logged in to pause a container')
        return redirect('login')
    else:
        success = pause_container(container_id, request.session['access_token'])
        return redirect('index')

def unpause_container_view(request):
    container_id = request.POST.get('container_id')    
    if 'access_token' not in request.session:
        messages.error(request, 'You must be logged in to unpause a container')
        return redirect('login')
    else:
        success = unpause_container(container_id, request.session['access_token'])
        return redirect('index')
    
def start_container_view(request):
    container_id = request.POST.get('container_id')    
    if 'access_token' not in request.session:
        messages.error(request, 'You must be logged in to unpause a container')
        return redirect('login')
    else:
        success = start_container(container_id, request.session['access_token'])
        return redirect('index')
    
def edit_container_view(request):
    ContainerID = request.POST.get('container_id') 
    NewRam = int(request.POST.get('NewRam'))   
    if 'access_token' not in request.session:
        messages.error(request, 'You must be logged in to unpause a container')
        return redirect('login')
    else:
        success = edit_container(ContainerID, NewRam, request.session['access_token'])
        return redirect('index')
    
def profile(request):
    if 'user' in request.session:
        return render(request, 'account.html', {'user': request.session['user']})
    else:
        return redirect('login')
    
def logs(request):
    if 'user' in request.session:
        container_id = request.POST.get('container_id')
        print("1", container_id)
        try:
            log_list = requests.get(f'{LOG_URL}/log/{container_id}', headers={'Authorization': f'Bearer {request.session["access_token"]}'})
            print("Hello", container_id)
            if log_list.status_code == 200:
                data = log_list.json()
                print("Hello", data)
                return render(request, 'logs.html', {'user': request.session['user'], 'logs': data})
            else:
                return render(request, 'logs.html', {'user': request.session['user']})
        except Exception as e:
            print(e)
            return render(request, 'logs.html', {'user': request.session['user']})