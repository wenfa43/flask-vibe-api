from datetime import datetime, timezone

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException


app = Flask(__name__)
app.json.ensure_ascii = False

tasks = []
next_task_id = 1

HTTP_ERROR_TRANSLATIONS = {
    400: "請求錯誤",
    401: "未經授權",
    403: "禁止存取",
    404: "找不到資源",
    405: "不允許此 HTTP 方法",
    406: "無法接受的格式",
    408: "請求逾時",
    409: "發生衝突",
    410: "資源已不存在",
    413: "請求內容過大",
    414: "請求網址過長",
    415: "不支援的媒體類型",
    422: "無法處理的內容",
    429: "請求過於頻繁",
    500: "伺服器內部錯誤",
    501: "尚未支援此功能",
    502: "閘道錯誤",
    503: "服務暫時無法使用",
    504: "閘道逾時",
}


def bilingual_message(english, traditional_chinese):
    return f"{english} / {traditional_chinese}"


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
    message = bilingual_message(
        error.description,
        HTTP_ERROR_TRANSLATIONS.get(error.code, "HTTP 錯誤"),
    )
    return make_response("error", message, None, error.code)


@app.get("/api/health")
def health_check():
    return make_response(
        "success",
        bilingual_message("Server is running", "伺服器運作中"),
        {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        200,
    )


@app.get("/api/tasks")
def get_tasks():
    return make_response(
        "success",
        bilingual_message("Tasks retrieved successfully", "已成功取得任務"),
        tasks,
        200,
    )


@app.post("/api/tasks")
def create_task():
    global next_task_id

    if not request.is_json:
        return make_response(
            "error",
            bilingual_message(
                "Request body must be valid JSON",
                "請求本文必須是有效的 JSON",
            ),
            None,
            400,
        )

    payload = request.get_json()
    if not isinstance(payload, dict):
        return make_response(
            "error",
            bilingual_message("JSON body must be an object", "JSON 本文必須是物件"),
            None,
            400,
        )

    title = payload.get("title")
    if not isinstance(title, str) or not title.strip():
        return make_response(
            "error",
            bilingual_message(
                "A non-empty title is required",
                "標題為必填欄位，且不可為空",
            ),
            None,
            400,
        )

    task = {
        "id": next_task_id,
        "title": title,
        "description": payload.get("description", ""),
    }
    tasks.append(task)
    next_task_id += 1

    return make_response(
        "success",
        bilingual_message("Task created successfully", "已成功建立任務"),
        task,
        201,
    )


@app.get("/api/tasks/<int:task_id>")
def get_task(task_id):
    task = next((task for task in tasks if task["id"] == task_id), None)
    if task is None:
        return make_response(
            "error",
            bilingual_message("Task not found", "找不到任務"),
            None,
            404,
        )

    return make_response(
        "success",
        bilingual_message("Task retrieved successfully", "已成功取得任務"),
        task,
        200,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
