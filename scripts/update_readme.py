#!/usr/bin/env python3
"""
Скрипт для автоматического обновления README профиля
Подтягивает описание проектов из их README файлов
"""

import os
import re
import base64
import requests
from pathlib import Path

# Конфигурация
USERNAME = "zxcblazee"
REPO_NAME = "zxcblazee"
PROJECTS = [
    {"name": "FinanceTracker", "repo": "FinanceTracker"},
    {"name": "ServiceCenterWPF", "repo": "ServiceCenterWPF"},
    # Добавь сюда свои проекты
]

def get_readme_content(owner, repo):
    """Получает содержимое README репозитория через GitHub API"""
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        content = data.get("content", "")
        decoded = base64.b64decode(content).decode("utf-8")
        return decoded
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка получения README для {repo}: {e}")
        return None

def extract_project_info(readme_content):
    """
    Извлекает из README проекта:
    - Заголовок (первый h1 или h2)
    - Краткое описание (первые 1-2 предложения)
    - Стек технологий (если есть)
    """
    if not readme_content:
        return None
    
    lines = readme_content.split("\n")
    
    # Ищем заголовок
    title = None
    description = []
    tech_stack = []
    
    for i, line in enumerate(lines):
        # Ищем заголовок
        if line.startswith("# "):
            title = line.replace("# ", "").strip()
        elif line.startswith("## "):
            title = line.replace("## ", "").strip()
        
        # Ищем описание (не пустые строки после заголовка)
        if i > 0 and not line.startswith("#") and line.strip() and not line.startswith("!["):
            if not description:
                description.append(line.strip())
            elif len(description) < 2:
                description.append(line.strip())
    
    # Если не нашли заголовок, берем имя репозитория
    if not title:
        title = "Проект"
    
    return {
        "title": title,
        "description": " ".join(description)[:150] + "..." if description else "Описание отсутствует"
    }

def generate_projects_block():
    """Генерирует HTML-блок с проектами"""
    projects_html = []
    projects_html.append('<div align="center">')
    projects_html.append('  <h1>Projects</h1>')
    projects_html.append('</div>')
    projects_html.append('')
    projects_html.append('| Название | Описание |')
    projects_html.append('|----------|----------|')
    
    for project in PROJECTS:
        readme = get_readme_content(USERNAME, project["repo"])
        info = extract_project_info(readme) if readme else None
        
        if info:
            # Создаем ссылку на репозиторий
            repo_url = f"https://github.com/{USERNAME}/{project['repo']}"
            title = info["title"]
            desc = info["description"]
            
            projects_html.append(f"| **[**`{project['name']}`**]({repo_url})** | {desc} |")
        else:
            # Если README не найден, показываем базовую информацию
            repo_url = f"https://github.com/{USERNAME}/{project['repo']}"
            projects_html.append(f"| **[**`{project['name']}`**]({repo_url})** | *(README не найден)* |")
    
    return "\n".join(projects_html)

def update_readme():
    """Обновляет главный README файл"""
    script_dir = Path(__file__).parent.parent
    template_path = script_dir / "templates" / "readme_template.md"
    readme_path = script_dir / "README.md"
    
    # Читаем шаблон
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    
    # Генерируем блок с проектами
    projects_block = generate_projects_block()
    
    # Вставляем блок между маркерами
    pattern = r'(<!-- PROJECTS_START -->)(.*?)(<!-- PROJECTS_END -->)'
    replacement = r'\1\n' + projects_block + '\n\3'
    
    new_readme = re.sub(pattern, replacement, template, flags=re.DOTALL)
    
    # Сохраняем обновленный README
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_readme)
    
    print("✅ README успешно обновлен!")

if __name__ == "__main__":
    update_readme()
