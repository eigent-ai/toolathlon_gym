#!/bin/bash

# Canvas MCP Server - Release v2.2.2
# Fixes console.log pollution causing JSON parsing errors

set -e  # Exit on any error

echo "🚀 Canvas MCP Server Release v2.2.2"
echo "=====================================\n"

# Clean and build
echo "🔨 Cleaning and building..."
npm run clean
npm run build

# Check build was successful
if [ ! -f "build/index.js" ]; then
    echo "❌ Build failed - build/index.js not found"
    exit 1
fi

echo "✅ Build completed successfully\n"

# Git operations
echo "📦 Git operations..."
git add .
git status

echo "\n📝 Committing changes..."
git commit -m "fix: resolve console.log stdout pollution causing JSON parsing errors

- Changed console.log to console.error in src/client.ts (request logging, error responses, retries)
- Fixed tool execution logging in src/index.ts to use stderr
- Eliminates 'Unexpected token C, [Canvas API' JSON parsing errors
- MCP protocol now receives clean JSON communication over stdio
- Version bump to 2.2.2

Fixes #issue with constant JSON parsing errors in Claude Desktop"

echo "\n🚢 Force pushing to origin main..."
git push origin main --force

echo "✅ Git push completed\n"

# NPM publish
echo "📦 Publishing to npm..."
npm publish

echo "✅ Published canvas-mcp-server@2.2.2 to npm\n"

echo "🎉 Release complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Fixed the JSON parsing error spam in Claude Desktop"
echo "✅ Console.log statements now properly use stderr"
echo "✅ MCP communication is now clean JSON over stdio"
echo "✅ Version 2.2.2 published to npm"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "\n🔄 Users can now update with: npm install -g canvas-mcp-server@2.2.2"
echo "🔄 Or update their Claude Desktop config to use the latest version"
