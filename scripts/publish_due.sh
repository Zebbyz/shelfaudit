#!/usr/bin/env bash
# Daily blog publish: builds posts dated on or before today (Pacific/Auckland), commits, pushes, deploys.
set -euo pipefail
cd "$(dirname "$0")/.."
git checkout -q intel && git pull -q --rebase origin intel
python3 scripts/build_blog.py
if [ -n "$(git status --porcelain public/blog)" ]; then
  git add public/blog && git commit -qm "Blog: publish posts due $(TZ=Pacific/Auckland date +%F)" && git push -q origin intel
  npx wrangler pages deploy public --project-name shelfaudit --branch intel --commit-dirty=true
else echo "No new posts due"; fi
