from http.client import HTTPResponse
from django.shortcuts import redirect, render
import requests
from django.contrib import messages
# Create your views here.
def index(request):
    if 'user' in request.session:
        print(request.session['user'])
        return render(request, 'index.html', {'user': request.session['user']})
    else:
        return redirect('login')
    
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        headers = {'Content-Type': 'application/json'}
        response = requests.post('http://localhost:4000/login', headers=headers, json={'email': email, 'password': password})
        data = response.json()
        if 'access_token' in data and 'refresh_token' in data:
            request.session['access_token'] = data['access_token']
            request.session['refresh_token'] = data['refresh_token']
            request.session['user'] = data['user']
            print(request.session['user'])
            return redirect('index')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        headers = {'Content-Type': 'application/json'}
        response = requests.post('http://localhost:4000/register', headers=headers, json={'email': email, 'username': username, 'password': password})
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
            response = requests.post('http://localhost:4000/payment/charge', headers=headers, json=body)
            data = response.json()
            if 'message' in data:
                messages.success(request, data['data'].get('actions')[1].get('url'))
                # print(data['data'].get('actions')[1].get('url'))
                return redirect(data['data'].get('actions')[1].get('url'))
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
            ram = int(request.POST.get('ram'))
            core = int(request.POST.get('core'))
            headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {request.session["access_token"]}'}
            body = {"ContainerName": container_name, "ContainerRam": ram, "ContainerCore": core}
            print(body)
            response = requests.post('http://103.181.182.243:8080/container/create', headers=headers, json=body)
            if response.status_code == 200:
                data = response.json()
                if 'container_Id' in data:
                    request.session['container_Id'] = data['container_Id']
                    request.session[data['container_Id']] = data['ssh_port']
                    print(data)
                    messages.success(request, 'Container created successfully')
                    return redirect('index')
                else:
                    messages.error(request, 'Failed to create container')
                    return redirect('index')
            else:
                messages.error(request, 'Failed to create container')
                print(response.json())
                return redirect('index')
    return redirect('index')