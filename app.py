import os
from flask import Flask, render_template, request, jsonify
from github_helper import GitHubProfessionalizer
from github import GithubException

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production")

# Token set once in Render environment variables — never exposed to the browser
SERVER_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()


def _get_professionalizer(req):
    # Prefer server-side env token; fall back to token sent from browser
    token = SERVER_TOKEN or req.json.get("token", "").strip()
    if not token:
        return None, jsonify({"error": "GitHub token is required"}), 400
    try:
        gp = GitHubProfessionalizer(token)
        _ = gp.user.login          # validate token early
        return gp, None, None
    except GithubException as e:
        return None, jsonify({"error": f"Invalid token or GitHub error: {e.data}"}), 401


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", token_configured=bool(SERVER_TOKEN))


@app.route("/api/token-status")
def token_status():
    """Let the frontend know if a server-side token is already configured."""
    return jsonify({"configured": bool(SERVER_TOKEN)})


@app.route("/api/audit", methods=["POST"])
def audit():
    gp, err, code = _get_professionalizer(request)
    if err:
        return err, code
    try:
        data = gp.audit_repos()
        return jsonify(data)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/update-readme", methods=["POST"])
def update_readme():
    gp, err, code = _get_professionalizer(request)
    if err:
        return err, code
    skills      = request.json.get("skills", [])
    linkedin    = request.json.get("linkedin", "")
    formspree   = request.json.get("formspree_id", "")
    try:
        data = gp.update_profile_readme(
            skills=skills,
            linkedin=linkedin,
            formspree_id=formspree,
        )
        return jsonify(data)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/enhance-repos", methods=["POST"])
def enhance_repos():
    gp, err, code = _get_professionalizer(request)
    if err:
        return err, code
    repos = request.json.get("repos", [])
    if not repos:
        return jsonify({"error": "No repositories selected"}), 400
    try:
        data = gp.enhance_repos(repos)
        return jsonify(data)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
