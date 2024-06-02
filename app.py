from flask import Flask, jsonify, request
from docker_events import log_event

app = Flask(__name__)

# @app.route('/events', methods=['GET'])
# def get_events():
#     try:
#         with open("docker_events.log", "r") as log_file:
#             content = log_file.read()
#         return content, 200
#     except FileNotFoundError:
#         return jsonify({"error": "Log file does not exist yet."}), 404

@app.route('/events', methods=['POST'])
def start_events():
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    docker_events.start_event_logging(user_id)
    return jsonify({"status": "Event logging started", "user_id": user_id}), 200

@app.route('/log', methods=['GET'])
def get_log_file():
    try:
        with open("docker_events.log", "r") as log_file:
            lines = log_file.readlines()
            # Parse each log entry and create JSON objects
            log_entries = []
            for line in lines:
                parts = line.strip().split(";")
                if len(parts) == 6:
                    date, time, user_id, container_name, container_id, action = parts
                    log_entry = {
                        "date": date,
                        "time": time,
                        "user_id":user_id,
                        "container_name": container_name,
                        "container_id": container_id,
                        "action": action
                    }
                    log_entries.append(log_entry)
            return jsonify(log_entries), 200
    except FileNotFoundError:
        return jsonify({"error": "Log file does not exist yet."}), 404

@app.route('/log', methods=['POST'])
def get_log_file_by_container_id():
    try:
        data = request.get_json()
        container_id = data.get('container_id')
        if not container_id:
            return jsonify({"error": "Container ID is required"}), 400

        with open("docker_events.log", "r") as log_file:
            lines = log_file.readlines()
            # Parse each log entry and filter by container ID
            log_entries = []
            for line in lines:
                parts = line.strip().split(";")
                if len(parts) == 5:
                    date, time, container_name, log_container_id, action = parts
                    if log_container_id == container_id:
                        log_entry = {
                            "date": date,
                            "time": time,
                            "container_name": container_name,
                            "container_id": log_container_id,
                            "action": action
                        }
                        log_entries.append(log_entry)
            return jsonify(log_entries), 200
    except FileNotFoundError:
        return jsonify({"error": "Log file does not exist yet."}), 404

@app.route('/log/<container_id>', methods=['GET'])
def get_log_file_by_container_id(container_id):
    try:
        with open("docker_events.log", "r") as log_file:
            lines = log_file.readlines()
            log_entries = []
            for line in lines:
                parts = line.strip().split(";")
                if len(parts) == 6:  # Including user_id
                    date, time, user_id, container_name, log_container_id, action = parts
                    if log_container_id == container_id:
                        log_entry = {
                            "date": date,
                            "time": time,
                            "user_id": user_id,
                            "container_name": container_name,
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


