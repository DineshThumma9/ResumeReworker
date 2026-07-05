#!/bin/bash

echo "==================================="
echo "🎨 Formatting ResumeReworker..."
echo "==================================="

# 1. Format Frontend (TypeScript/React/Tailwind)
echo ""
echo "📦 Formatting Frontend..."
cd frontend || exit 1

# Run eslint fix if possible
npm run lint -- --fix

# Use prettier to format the codebase (using npx so it downloads temporarily if not installed)
npx prettier --write "src/**/*.{ts,tsx,js,jsx,css}" "*.json"

cd ..

# 2. Format Backend (Python)
echo ""
echo "🐍 Formatting Backend..."
cd backend || exit 1

# Use uvx (uv tool) to run ruff (very fast python linter/formatter)
# Fix auto-fixable lint errors
uvx ruff check --extend-select I --fix .
# Format code
uvx ruff format .

cd ..

echo ""
echo "✨ All done! Both frontend and backend are formatted."
