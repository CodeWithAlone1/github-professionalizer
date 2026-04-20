# 🚀 GitHub Professionalizer

A Flask web app that automatically upgrades your GitHub profile in 3 steps:

1. **Audit** — scores every repo (README, description, license, topics, activity)
2. **Profile README** — generates & pushes a polished `username/username` README
3. **Enhance Repos** — auto-adds missing descriptions, topics, and MIT license

---

## 📁 Project Structure

```
github_pro/
├── app.py              # Flask routes
├── github_helper.py    # All GitHub API logic
├── templates/
│   └── index.html      # Dashboard UI
├── requirements.txt
├── Procfile            # Heroku
└── railway.toml        # Railway
```

---

## 🔑 GitHub Token

Create a token at:
**GitHub → Settings → Developer Settings → Personal access tokens → Tokens (classic)**

Required scopes: `repo`, `user`, `read:user`

---

## 🛠️ Run Locally

```bash
git clone <this-repo>
cd github_pro

pip install -r requirements.txt

python app.py
# Open http://localhost:5000
```

---

## ☁️ Deploy to Railway (recommended — free tier)

1. Push this folder to a GitHub repo
2. Go to [railway.app](https://railway.app) → **New Project → Deploy from GitHub**
3. Select your repo → Railway auto-detects Python + `railway.toml`
4. Add env variable: `SECRET_KEY` = any random string
5. Done! Railway gives you a public URL

---

## ☁️ Deploy to Heroku

```bash
heroku login
heroku create your-app-name
heroku config:set SECRET_KEY=your-random-secret
git push heroku main
heroku open
```

---

## ⚙️ Environment Variables

| Variable     | Required | Description                        |
|--------------|----------|------------------------------------|
| `SECRET_KEY` | Yes      | Flask session secret (any string)  |
| `PORT`       | Auto     | Set by Heroku/Railway automatically|

> **Never** commit your GitHub token. It's entered at runtime in the browser.
