from github import Github, GithubException
from datetime import datetime

# Auto-assign topics based on primary language
LANGUAGE_TOPICS = {
    'Python':     ['python', 'python3'],
    'JavaScript': ['javascript', 'nodejs'],
    'TypeScript': ['typescript'],
    'Java':       ['java'],
    'Go':         ['golang'],
    'Rust':       ['rust'],
    'C++':        ['cpp'],
    'C#':         ['csharp', 'dotnet'],
    'Ruby':       ['ruby'],
    'PHP':        ['php'],
    'Swift':      ['swift', 'ios'],
    'Kotlin':     ['kotlin', 'android'],
    'HTML':       ['html', 'web'],
    'CSS':        ['css', 'frontend'],
    'Shell':      ['bash', 'shell-script'],
}

MIT_LICENSE_TEMPLATE = """MIT License

Copyright (c) {year} {name}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


class GitHubProfessionalizer:
    def __init__(self, token: str):
        self.g = Github(token)
        self.user = self.g.get_user()

    # ─────────────────────────────────────────────
    # 1. AUDIT
    # ─────────────────────────────────────────────
    def audit_repos(self) -> dict:
        """Score every non-fork repo and return a list of issues."""
        repos_data = []
        for repo in self.user.get_repos():
            if repo.fork:
                continue

            score = 0
            issues = []

            # README (25 pts)
            has_readme = False
            try:
                repo.get_readme()
                has_readme = True
                score += 25
            except Exception:
                issues.append("Missing README.md")

            # Description (20 pts)
            has_desc = bool(repo.description)
            if has_desc:
                score += 20
            else:
                issues.append("No description set")

            # License (20 pts)
            has_license = repo.license is not None
            if has_license:
                score += 20
            else:
                issues.append("No license file")

            # Topics (20 pts)
            topics = repo.get_topics()
            has_topics = len(topics) > 0
            if has_topics:
                score += 20
            else:
                issues.append("No topics / tags")

            # Recent activity (15 pts)
            days_since = (datetime.utcnow() - repo.pushed_at.replace(tzinfo=None)).days
            is_recent = days_since < 180
            if is_recent:
                score += 15
            else:
                issues.append(f"No activity for {days_since} days")

            repos_data.append({
                "name":        repo.name,
                "url":         repo.html_url,
                "score":       score,
                "issues":      issues,
                "language":    repo.language or "—",
                "stars":       repo.stargazers_count,
                "has_readme":  has_readme,
                "has_desc":    has_desc,
                "has_license": has_license,
                "has_topics":  has_topics,
            })

        repos_data.sort(key=lambda r: r["score"])
        avg = sum(r["score"] for r in repos_data) // len(repos_data) if repos_data else 0
        return {"repos": repos_data, "avg_score": avg, "total": len(repos_data)}

    # ─────────────────────────────────────────────
    # 2. UPDATE PROFILE README  (Enhanced)
    # ─────────────────────────────────────────────

    # Map common skill names → skillicons.dev codes
    SKILL_MAP = {
        "python":"python","javascript":"js","typescript":"ts","java":"java",
        "go":"go","golang":"go","rust":"rust","c++":"cpp","cpp":"cpp",
        "c#":"cs","csharp":"cs","ruby":"ruby","php":"php","swift":"swift",
        "kotlin":"kotlin","html":"html","css":"css","shell":"bash","bash":"bash",
        "react":"react","vue":"vue","angular":"angular","nextjs":"nextjs",
        "nodejs":"nodejs","node":"nodejs","express":"express","django":"django",
        "flask":"flask","fastapi":"fastapi","spring":"spring",
        "docker":"docker","kubernetes":"kubernetes","k8s":"kubernetes",
        "aws":"aws","gcp":"gcp","azure":"azure","firebase":"firebase",
        "mongodb":"mongodb","postgres":"postgres","postgresql":"postgres",
        "mysql":"mysql","redis":"redis","sqlite":"sqlite",
        "git":"git","github":"github","linux":"linux","vscode":"vscode",
        "figma":"figma","tensorflow":"tensorflow","pytorch":"pytorch",
        "graphql":"graphql","tailwind":"tailwind","bootstrap":"bootstrap",
    }

    def _skills_icon_url(self, skills: list[str]) -> str:
        codes = []
        for s in skills:
            code = self.SKILL_MAP.get(s.lower().strip())
            if code and code not in codes:
                codes.append(code)
        if not codes:
            return ""
        return f"https://skillicons.dev/icons?i={','.join(codes)}&perline=12"

    def update_profile_readme(
        self,
        skills: list[str] | None = None,
        linkedin: str = "",
        formspree_id: str = "",
    ) -> dict:
        """Generate and push a stunning profile README with all enhancements."""
        u = self.user
        username = u.login
        own_repos = [r for r in u.get_repos() if not r.fork]
        total_stars = sum(r.stargazers_count for r in own_repos)

        # Auto-detect top languages if no skills provided
        lang_counts: dict[str, int] = {}
        for r in own_repos:
            if r.language:
                lang_counts[r.language] = lang_counts.get(r.language, 0) + 1
        auto_langs = [l for l, _ in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:8]]
        skill_list = skills if skills else auto_langs

        # Top repos
        top_repos = sorted(own_repos, key=lambda r: r.stargazers_count, reverse=True)[:3]
        repo_lines = "\n".join(
            f"| [{r.name}]({r.html_url}) | {r.description or '_No description_'} | ⭐ {r.stargazers_count} |"
            for r in top_repos
        )

        # ── Typing SVG header ─────────────────────────
        greeting_name = u.name or username
        typing_svg = (
            f"https://readme-typing-svg.demolab.com"
            f"?font=Fira+Code&size=28&duration=3000&pause=1000"
            f"&color=58A6FF&center=true&vCenter=true&width=600"
            f"&lines=Hi+I'm+{greeting_name.replace(' ', '+')}+%F0%9F%91%8B"
            f";Welcome+to+my+GitHub!;I+build+things+with+code+%F0%9F%9A%80"
        )

        # ── Trophies ──────────────────────────────────
        trophy_url = (
            f"https://github-profile-trophy.vercel.app/"
            f"?username={username}&theme=tokyonight&no-frame=true"
            f"&no-bg=true&row=1&column=7"
        )

        # ── Stats & Streak ────────────────────────────
        stats_url  = f"https://github-readme-stats.vercel.app/api?username={username}&show_icons=true&theme=tokyonight&hide_border=true&count_private=true"
        streak_url = f"https://github-readme-streak-stats.herokuapp.com/?user={username}&theme=tokyonight&hide_border=true"
        langs_url  = f"https://github-readme-stats.vercel.app/api/top-langs/?username={username}&layout=compact&theme=tokyonight&hide_border=true&langs_count=8"

        # ── Skills ────────────────────────────────────
        skills_icon_url = self._skills_icon_url(skill_list)
        skills_section = (
            f'<img src="{skills_icon_url}" alt="skills"/>'
            if skills_icon_url else
            "  ".join(f"`{s}`" for s in skill_list)
        )

        # ── Snake ─────────────────────────────────────
        snake_section = f"""<picture>
  <source media="(prefers-color-scheme: dark)"
          srcset="https://raw.githubusercontent.com/{username}/{username}/output/github-contribution-grid-snake-dark.svg">
  <source media="(prefers-color-scheme: light)"
          srcset="https://raw.githubusercontent.com/{username}/{username}/output/github-contribution-grid-snake.svg">
  <img alt="Snake animation" src="https://raw.githubusercontent.com/{username}/{username}/output/github-contribution-grid-snake.svg"/>
</picture>"""

        # ── Social badges ─────────────────────────────
        badges = []
        if linkedin:
            li = linkedin.rstrip("/").split("/")[-1]
            badges.append(f"[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/{li})")
        if u.blog:
            badges.append(f"[![Portfolio](https://img.shields.io/badge/Portfolio-FF5722?style=for-the-badge&logo=google-chrome&logoColor=white)]({u.blog})")
        if u.twitter_username:
            badges.append(f"[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/{u.twitter_username})")
        if u.email:
            badges.append(f"[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:{u.email})")
        badges_section = "\n".join(badges) if badges else "_Add your social links in GitHub settings!_"

        # ── Contact form ──────────────────────────────
        if formspree_id:
            contact_section = f"""### 📬 Send Me a Message

[![Contact Form](https://img.shields.io/badge/Contact%20Me-4CAF50?style=for-the-badge&logo=mail.ru&logoColor=white)](https://formspree.io/f/{formspree_id})"""
        else:
            contact_section = f"""### 📬 Get In Touch

[![Email Me](https://img.shields.io/badge/Email%20Me-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:{u.email or 'your@email.com'})"""

        # ── Assemble README ───────────────────────────
        readme = f"""<div align="center">
  <img src="{typing_svg}" alt="Typing SVG"/>
</div>

<div align="center">

{badges_section}

</div>

---

## 🏆 GitHub Trophies

<div align="center">

[![trophy]({trophy_url})](https://github.com/ryo-ma/github-profile-trophy)

</div>

---

## 📊 GitHub Stats

<div align="center">
  <img src="{stats_url}" height="170"/>
  <img src="{streak_url}" height="170"/>
</div>

<div align="center">
  <img src="{langs_url}" height="160"/>
</div>

---

## 💼 Tech Skills

<div align="center">

{skills_section}

</div>

---

## 🌟 Featured Projects

| Project | Description | Stars |
|---|---|:---:|
{repo_lines}

---

## 🐍 My Contributions

<div align="center">

{snake_section}

</div>

---

## 📫 Contact

<div align="center">

{contact_section}

</div>

---

<div align="center">
  <img src="https://komarev.com/ghpvc/?username={username}&label=Profile+Views&color=58a6ff&style=flat" alt="profile views"/>
  <br/>
  <sub>Last refreshed: {datetime.utcnow().strftime('%d %B %Y')} · Generated by GitHub Professionalizer</sub>
</div>
"""

        # Push to profile repo (username/username)
        profile_repo_name = self.user.login
        try:
            profile_repo = self.g.get_repo(f"{self.user.login}/{profile_repo_name}")
        except GithubException:
            profile_repo = self.user.create_repo(
                profile_repo_name,
                description="✨ My GitHub profile README",
                auto_init=True,
            )

        try:
            existing = profile_repo.get_readme()
            profile_repo.update_file(
                existing.path,
                "chore: update profile README via GitHub Professionalizer",
                readme,
                existing.sha,
            )
            action = "updated"
        except GithubException:
            profile_repo.create_file(
                "README.md",
                "feat: create profile README via GitHub Professionalizer",
                readme,
            )
            action = "created"

        return {"success": True, "action": action, "preview": readme}

    # ─────────────────────────────────────────────
    # 3. ENHANCE REPOS (desc + topics + license)
    # ─────────────────────────────────────────────
    def enhance_repos(self, repo_names: list[str]) -> dict:
        """Add missing descriptions, topics, and MIT license to chosen repos."""
        results = []
        for name in repo_names:
            try:
                repo = self.g.get_repo(f"{self.user.login}/{name}")
                actions = []

                # Description
                if not repo.description:
                    lang = repo.language or "software"
                    desc = f"A {lang} project"
                    repo.edit(description=desc)
                    actions.append(f"✅ Description added: \"{desc}\"")

                # Topics
                if not repo.get_topics() and repo.language:
                    new_topics = LANGUAGE_TOPICS.get(repo.language, [repo.language.lower()])
                    repo.replace_topics(new_topics)
                    actions.append(f"✅ Topics added: {', '.join(new_topics)}")

                # MIT License
                if not repo.license:
                    content = MIT_LICENSE_TEMPLATE.format(
                        year=datetime.utcnow().year,
                        name=self.user.name or self.user.login,
                    )
                    try:
                        repo.create_file(
                            "LICENSE",
                            "chore: add MIT license via GitHub Professionalizer",
                            content,
                        )
                        actions.append("✅ MIT LICENSE file added")
                    except GithubException:
                        actions.append("⚠️ LICENSE already exists (skipped)")

                if not actions:
                    actions.append("ℹ️ Repo already looks good — nothing to change")

                results.append({"repo": name, "success": True, "actions": actions})
            except Exception as exc:
                results.append({"repo": name, "success": False, "error": str(exc)})

        return {"results": results}
