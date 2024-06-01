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
            response = requests.post('http://localhost:4000/charge', headers=headers, json=body)
            data = response.json()
            if 'message' in data:
                messages.success(request, data['message'])
                return redirect('index')
    return render(request, 'recharge.html')

def logout(request):
    if 'user' in request.session:
        del request.session
        messages.success(request, 'You have been logged out')
        return redirect('login')