from flask import Flask, jsonify, request, Response
import logging
import os

# --- Config & logger ---
APP_NAME = "Flask Minimal CI/CD App"
VERSION = os.environ.get("APP_VERSION", "1.0.0")

logger = logging.getLogger("flask_app")
logger.setLevel(logging.INFO)
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(h)

app = Flask(__name__)

# --- In-memory demo data ---
tasks = [
    {"id": 1, "title": "Learn Docker", "completed": False},
    {"id": 2, "title": "CI/CD pipeline", "completed": True}
]

def next_id():
    return max([t["id"] for t in tasks] or [0]) + 1

# --- API endpoints ---
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)

@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.get_json() or {}
    title = data.get("title")
    if not title:
        return jsonify({"error":"title required"}), 400
    t = {"id": next_id(), "title": title, "completed": False}
    tasks.append(t)
    logger.info("Task created: %s", t)
    return jsonify(t), 201

@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json() or {}
    for t in tasks:
        if t["id"] == task_id:
            t["title"] = data.get("title", t["title"])
            t["completed"] = data.get("completed", t["completed"])
            logger.info("Task updated: %s", t)
            return jsonify(t)
    return jsonify({"error":"not found"}), 404

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t["id"] != task_id]
    logger.info("Task deleted: %s", task_id)
    return jsonify({"message":"deleted"})

# --- health & meta ---
@app.route("/health")
def health():
    return jsonify({"status":"healthy"}), 200

@app.route("/version")
def version():
    return jsonify({"version": VERSION})

# --- Single-file styled landing page (no static folder needed) ---
@app.route("/")
def index():
    html = f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
      <title>{APP_NAME}</title>
      <style>
        body{{font-family:Inter,system-ui,Arial; background:#071028;color:#e6eef7;margin:0;padding:0}}
        .wrap{{max-width:960px;margin:40px auto;padding:24px}}
        .hero{{background:linear-gradient(90deg,#7c3aed22,transparent);padding:28px;border-radius:12px}}
        h1{{
          margin:0 0 8px;font-size:28px;
        }}
        .lead{{color:#9aa4b2;margin-bottom:12px}}
        .btn{display:inline-block;padding:10px 14px;background:#7c3aed;color:#fff;border-radius:8px;text-decoration:none}
        .card{{margin-top:18px;padding:18px;background:#071529;border-radius:10px}}
        pre{{background:#041124;padding:12px;border-radius:8px;color:#9aa4b2;overflow:auto}}
      </style>
    </head>
    <body>
      <div class="wrap">
        <div class="hero">
          <h1>{APP_NAME}</h1>
          <p class="lead">Version: {VERSION} • Demo REST API (tasks) • Docker + CI/CD</p>
          <a class="btn" href="#api">Open API</a>
        </div>

        <div id="api" class="card">
          <h2>Quick demo</h2>
          <p>Load tasks from the API and try creating a new one.</p>
          <button onclick="load()" class="btn">Load tasks</button>
          <pre id="out">{{}}</pre>

          <h3>Create task</h3>
          <input id="title" placeholder="Task title" />
          <button onclick="create()" class="btn">Create</button>
        </div>

        <footer style="margin-top:18px;color:#9aa4b2">Made with ❤️ • Docker • GitHub Actions • Render</footer>
      </div>

      <script>
        async function load(){ 
          const res = await fetch('/api/tasks'); 
          const data = await res.json(); 
          document.getElementById('out').textContent = JSON.stringify(data,null,2);
        }
        async function create(){
          const title = document.getElementById('title').value || 'New task';
          const res = await fetch('/api/tasks',{method:'POST',headers:{{'Content-Type':'application/json'}}, body: JSON.stringify({{title}})});
          if(res.ok) load(); else alert('error');
        }
      </script>
    </body>
    </html>
    """
    return Response(html, mimetype="text/html")

if __name__ == "__main__":
    logger.info("Starting %s v%s", APP_NAME, VERSION)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
