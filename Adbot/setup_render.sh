#!/bin/bash
# Quick setup script for Render deployment

echo "🚀 Setting up for Render deployment..."
echo ""

# Check if git is initialized
if [ ! -d "../.git" ]; then
    echo "📦 Initializing Git repository..."
    cd ..
    git init
    git add .
    git commit -m "Initial commit for Render deployment"
    echo ""
    echo "✅ Git initialized!"
    echo ""
    echo "⚠️  Next steps:"
    echo "1. Create a repository on GitHub: https://github.com/new"
    echo "2. Run these commands (replace YOUR_USERNAME and YOUR_REPO_NAME):"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
    echo ""
    echo "3. Then go to Render.com and connect your repository"
else
    echo "✅ Git repository already initialized"
    echo ""
    echo "📝 Current git status:"
    cd ..
    git status
    echo ""
    echo "💡 To push to GitHub:"
    echo "   git add ."
    echo "   git commit -m 'Your commit message'"
    echo "   git push"
fi

echo ""
echo "📋 Remember: config.toml is in .gitignore (for security)"
echo "   You'll need to add it manually on Render using the Shell tab"
echo "   Or temporarily remove it from .gitignore to include it in Git"

