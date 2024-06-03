from flask import Flask, jsonify, request
# from docker_events import log_event, handle_docker_events
import jwt
from functools import wraps

SECRET_KEY = '1becc05fed3a8ef601b365a7ae8daed7a997856161e0876b9e1c535d89acaba8'

app = Flask(__name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except Exception as e:
            return jsonify({'message': 'Token is invalid!'}), 403
        print(data)
        return f(data['uuid'], *args, **kwargs)
    return decorated

# @app.route('/events', methods=['GET'])
# def get_events():
#     try:
#         with open("docker_events.log", "r") as log_file:
#             content = log_file.read()
#         return content, 200
#     except FileNotFoundError:
#         return jsonify({"error": "Log file does not exist yet."}), 404

@app.route('/events', methods=['POST'])
@token_required
def start_events(user_id):
    data = request.get_json()
    # handle_docker_events(user_id)
    return jsonify({"status": "Event logging started", "user_id": user_id}), 200

@app.route('/log/add', methods=['POST'])
@token_required
def add_log_entry(user_id):
    data = request.get_json()
    container_id = data.get('container_id')
    action = data.get('action')
    if not all([container_id, action]):
        return jsonify({"error": "Container ID, Container Name, and Action are required"}), 400

    from datetime import datetime
    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")

    log_entry = f"{date};{time};{user_id};{container_id};{action}\n"

    with open("docker_events.log", "a") as log_file:
        log_file.write(log_entry)

    return jsonify({"message": "Log entry added successfully"}), 201

@app.route('/log', methods=['GET'])
@token_required
def get_log_file(user_id):
    try:
        with open("docker_events.log", "r") as log_file:
            lines = log_file.readlines()
            # Parse each log entry and create JSON objects
            log_entries = []
            for line in lines:
                parts = line.strip().split(";")
                if len(parts) == 5:
                    date, time, log_user_id, container_id, action = parts
                    if str(user_id) == log_user_id:
                        log_entry = {
                            "date": date,
                            "time": time,
                            "user_id":log_user_id,
                            "container_id": container_id,
                            "action": action
                        }
                        log_entries.append(log_entry)
            return jsonify(log_entries), 200
    except FileNotFoundError:
        return jsonify({"error": "Log file does not exist yet."}), 404

@app.route('/log', methods=['POST'])
@token_required
def get_log_file_by_container_id_post(user_id):
    data = request.get_json()
    container_id = data.get('container_id')
    if not container_id:
        return jsonify({"error": "Container ID is required"}), 400
    try:
        with open("docker_events.log", "r") as log_file:
            lines = log_file.readlines()
            log_entries = []
            for line in lines:
                parts = line.strip().split(";")
                if len(parts) == 5:  # Including user_id
                    date, time, log_user_id, container_name, log_container_id, action = parts
                    if log_container_id == container_id:
                        log_entry = {
                            "date": date,
                            "time": time,
                            "user_id": log_user_id,
                            "container_id": log_container_id,
                            "action": action
                        }
                        log_entries.append(log_entry)
            return jsonify(log_entries), 200
    except FileNotFoundError:
        return jsonify({"error": "Log file does not exist yet."}), 404

@app.route('/log/<container_id>', methods=['GET'])
@token_required
def get_log_file_by_container_id(user_id, container_id):
    try:
        with open("docker_events.log", "r") as log_file:
            lines = log_file.readlines()
            log_entries = []
            for line in lines:
                parts = line.strip().split(";")
                if len(parts) == 5:  # Including user_id
                    date, time, log_user_id, log_container_id, action = parts
                    if log_container_id == container_id:
                        log_entry = {
                            "date": date,
                            "time": time,
                            "user_id": log_user_id,
                            "container_id": log_container_id,
                            "action": action
                        }
                        log_entries.append(log_entry)
            return jsonify(log_entries), 200
    except FileNotFoundError:
        return jsonify({"error": "Log file does not exist yet."}), 404

if __name__ == '__main__':
    app.run(debug=True)#, host='0.0.0.0')

# Contoh penggunaan:
# curl -X POST -H "Content-Type: application/json" -d '{"user_id": "user123"}' http://localhost:5000/events
# curl http://localhost:5000/log
# curl http://localhost:5000/log/<container_id>


