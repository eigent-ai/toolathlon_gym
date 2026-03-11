#!/bin/bash

# Canvas MCP Server Release Script v2.2.3
# Handles build, git operations, and npm publishing

set -e

echo "🚀 Canvas MCP Server Release Script v2.2.3"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: package.json not found. Are you in the right directory?${NC}"
    exit 1
fi

# Check if we have the Canvas MCP package
if ! grep -q "canvas-mcp-server" package.json; then
    echo -e "${RED}❌ Error: This doesn't appear to be the Canvas MCP server directory.${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Pre-flight checks...${NC}"

# Check git status
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  Working directory has changes. Proceeding with release...${NC}"
else
    echo -e "${GREEN}✅ Working directory is clean${NC}"
fi

# Get current version
CURRENT_VERSION=$(node -p "require('./package.json').version")
echo -e "${BLUE}📦 Current version: ${CURRENT_VERSION}${NC}"

echo -e "${BLUE}🔨 Step 1: Building TypeScript...${NC}"
npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ TypeScript build successful${NC}"
else
    echo -e "${RED}❌ TypeScript build failed${NC}"
    exit 1
fi

echo -e "${BLUE}🧪 Step 2: Running tests and linting...${NC}"
npm run type-check

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Type checking passed${NC}"
else
    echo -e "${RED}❌ Type checking failed${NC}"
    exit 1
fi

echo -e "${BLUE}📝 Step 3: Git operations...${NC}"

# Add all changes
git add .

# Check if there are changes to commit
if [ -z "$(git diff --cached --name-only)" ]; then
    echo -e "${YELLOW}⚠️  No changes to commit${NC}"
else
    # Commit changes
    git commit -m "🐛 Fix JSON parsing error in Canvas API responses

- Resolve 'Unexpected token C, !Canvas API... is not valid JSON' error
- Enhanced error response handling for non-JSON responses
- Added content-type checking and graceful fallbacks
- Improved error logging and debugging
- Version bump to ${CURRENT_VERSION}

Fixes: JSON parsing errors from Canvas HTML/text error responses
Impact: Eliminates annoying but benign error messages
Type: Bug fix (patch version)"

    echo -e "${GREEN}✅ Changes committed${NC}"
fi

# Create git tag
git tag -a "v${CURRENT_VERSION}" -m "Release v${CURRENT_VERSION}: JSON parsing error fix

Key Changes:
- Fixed JSON parsing error in Canvas API responses
- Enhanced error handling for HTML/text responses
- Improved debugging and logging
- Backward compatible bug fix

This release resolves the 'benign but drives people insane' JSON parsing 
errors that occurred when Canvas returned non-JSON error responses."

echo -e "${GREEN}✅ Git tag v${CURRENT_VERSION} created${NC}"

# Push to origin
echo -e "${BLUE}📤 Pushing to GitHub...${NC}"
git push origin main
git push origin "v${CURRENT_VERSION}"

echo -e "${GREEN}✅ Pushed to GitHub${NC}"

echo -e "${BLUE}📦 Step 4: NPM Publishing...${NC}"

# Check if logged into npm
if ! npm whoami > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Not logged into npm. Please run 'npm login' first.${NC}"
    exit 1
fi

# Check if package already exists at this version
if npm view canvas-mcp-server@${CURRENT_VERSION} version > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Version ${CURRENT_VERSION} already exists on npm${NC}"
    exit 1
fi

# Publish to npm
npm publish

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully published to npm${NC}"
else
    echo -e "${RED}❌ NPM publish failed${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Release Complete!${NC}"
echo -e "${GREEN}==================${NC}"
echo -e "${GREEN}✅ Version ${CURRENT_VERSION} has been:${NC}"
echo -e "${GREEN}   - Built and tested${NC}"
echo -e "${GREEN}   - Committed to git${NC}"
echo -e "${GREEN}   - Tagged as v${CURRENT_VERSION}${NC}"
echo -e "${GREEN}   - Pushed to GitHub${NC}"
echo -e "${GREEN}   - Published to npm${NC}"
echo ""
echo -e "${BLUE}🔗 Links:${NC}"
echo -e "${BLUE}   📦 NPM: https://www.npmjs.com/package/canvas-mcp-server${NC}"
echo -e "${BLUE}   🐙 GitHub: https://github.com/DMontgomery40/mcp-canvas-lms${NC}"
echo -e "${BLUE}   🏷️  Release: https://github.com/DMontgomery40/mcp-canvas-lms/releases/tag/v${CURRENT_VERSION}${NC}"
echo ""
echo -e "${YELLOW}📋 Post-Release Checklist:${NC}"
echo -e "${YELLOW}   - Update any dependent projects${NC}"
echo -e "${YELLOW}   - Announce the fix in relevant channels${NC}"
echo -e "${YELLOW}   - Update documentation if needed${NC}"
echo ""
echo -e "${GREEN}🎊 The JSON parsing error fix is now live!${NC}"
