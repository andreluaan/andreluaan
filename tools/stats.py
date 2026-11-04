"""Collect public GitHub numbers for the stats card into data/stats.json.

Runs locally or in the daily Action; GITHUB_TOKEN is optional (raises the rate limit).
"""
import json, os, re, urllib.request
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

USER = 'andreluaan'
OUT = Path(__file__).resolve().parent.parent / 'data/stats.json'


def get(url, raw=False):
    headers = {'User-Agent': 'sumi-profile-stats'}
    if os.environ.get('GITHUB_TOKEN') and 'api.github.com' in url:
        headers['Authorization'] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as response:
        body = response.read().decode()
    return body if raw else json.loads(body)


def contributions():
    page = get(f'https://github.com/users/{USER}/contributions', raw=True)
    dates = dict(re.findall(r'data-date="([\d-]+)" id="(contribution-day-component-[\d-]+)"', page))
    dates = {cell: day for day, cell in dates.items()}
    days = {}
    for cell, text in re.findall(r'for="(contribution-day-component-[\d-]+)"[^>]*>([^<]*)', page):
        match = re.match(r'(\d+) contribution', text)
        days[dates[cell]] = int(match.group(1)) if match else 0
    ordered = sorted(days.items())
    longest = run = 0
    for _, count in ordered:
        run = run + 1 if count else 0
        longest = max(longest, run)
    current = 0
    # Today may still be empty, so the streak counts back from yesterday in that case
    for index, (_, count) in enumerate(reversed(ordered)):
        if count:
            current += 1
        elif index > 0:
            break
    weeks = [sum(c for _, c in ordered[i:i + 7]) for i in range(0, len(ordered), 7)]
    best = max(ordered, key=lambda item: item[1])
    return dict(total=sum(days.values()), current=current, longest=longest, weeks=weeks, best_day=best[1])


def repositories():
    repos = [r for r in get(f'https://api.github.com/users/{USER}/repos?per_page=100') if not r['fork']]
    languages = Counter()
    for repo in repos:
        languages.update(get(repo['languages_url']))
    total = sum(languages.values()) or 1
    top = [(name, round(size / total, 3)) for name, size in languages.most_common(6)]
    return dict(repos=len(repos), stars=sum(r['stargazers_count'] for r in repos), languages=top)


if __name__ == '__main__':
    OUT.parent.mkdir(exist_ok=True)
    data = {**contributions(), **repositories(), 'updated': date.today().isoformat()}
    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding='utf8')
    print({k: v for k, v in data.items() if k != 'weeks'})
