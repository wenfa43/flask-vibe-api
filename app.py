from datetime import datetime, timezone

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException


app = Flask(__name__)
app.json.ensure_ascii = False

tasks = []
next_task_id = 1


def make_response(status, message, data, http_status):
    return jsonify(
        {
            "status": status,
            "message": message,
            "data": data,
        }
    ), http_status


@app.errorhandler(HTTPException)
def handle_http_error(error):
    return make_response("error", error.description, None, error.code)


@app.get("/api/health")
def health_check():
    return make_response(
        "success",
        "Server is running",
        {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        200,
    )


@app.get("/api/tasks")
def get_tasks():
    return make_response("success", "Tasks retrieved successfully", tasks, 200)


@app.post("/api/tasks")
def create_task():
    global next_task_id

    if not request.is_json:
        return make_response("error", "Request body must be valid JSON", None, 400)

    payload = request.get_json()
    if not isinstance(payload, dict):
        return make_response("error", "JSON body must be an object", None, 400)

    title = payload.get("title")
    if not isinstance(title, str) or not title.strip():
        return make_response("error", "A non-empty title is required", None, 400)

    task = {
        "id": next_task_id,
        "title": title,
        "description": payload.get("description", ""),
    }
    tasks.append(task)
    next_task_id += 1

    return make_response("success", "Task created successfully", task, 201)


@app.get("/api/tasks/<int:task_id>")
def get_task(task_id):
    task = next((task for task in tasks if task["id"] == task_id), None)
    if task is None:
        return make_response("error", "Task not found", None, 404)

    return make_response("success", "Task retrieved successfully", task, 200)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
