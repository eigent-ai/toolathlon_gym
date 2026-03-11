# Release Instructions for Canvas MCP Server v2.2.1

## 🚀 Automated Release (Recommended)

The easiest way to release is using the automated script:

```bash
# Make sure you're logged into npm first
npm login

# Run the automated release script
chmod +x release.sh
./release.sh

# Or via npm script
npm run release
```

## 📋 Manual Release Process

If you prefer to do it manually:

### 1. Build and Test
```bash
# Build TypeScript
npm run build

# Run type checking
npm run type-check

# Optional: Run a dry run first
npm run release:dry-run
```

### 2. Git Operations
```bash
# Add all changes
git add .

# Commit with descriptive message
git commit -m "🐛 Fix JSON parsing error in Canvas API responses

- Resolve 'Unexpected token C, !Canvas API... is not valid JSON' error  
- Enhanced error response handling for non-JSON responses
- Added content-type checking and graceful fallbacks
- Improved error logging and debugging
- Version bump to 2.2.1

Fixes: JSON parsing errors from Canvas HTML/text error responses
Impact: Eliminates annoying but benign error messages
Type: Bug fix (patch version)"

# Create and push tag
git tag -a "v2.2.1" -m "Release v2.2.1: JSON parsing error fix"
git push origin main
git push origin v2.2.1
```

### 3. NPM Publishing
```bash
# Make sure you're logged in
npm whoami

# Publish to npm
npm publish
```

## 🎯 What This Release Fixes

This v2.2.1 release specifically addresses:

- **JSON Parsing Error**: Fixes `Unexpected token 'C', "!Canvas API..." is not valid JSON`
- **Error Handling**: Better processing of Canvas HTML/text error responses  
- **Debugging**: Improved error messages and logging
- **Stability**: More robust handling of various Canvas API response types

## 🔍 Verification

After release, verify:

1. **NPM Package**: https://www.npmjs.com/package/canvas-mcp-server
2. **GitHub Release**: https://github.com/DMontgomery40/mcp-canvas-lms/releases
3. **Installation Test**: `npm install -g canvas-mcp-server@2.2.1`

## 📝 Release Notes

### v2.2.1 (2025-06-27)
- 🐛 **Fixed**: Critical JSON parsing error that occurred with Canvas API error responses
- 🔧 **Enhanced**: Error response handling for HTML/text responses from Canvas
- 📊 **Improved**: Debugging and logging capabilities
- ✅ **Impact**: Eliminates "benign but drives people insane" error messages
- 🔄 **Compatibility**: Fully backward compatible, no breaking changes

## 🚨 Pre-Release Checklist

- [x] Version bumped in package.json (2.2.0 → 2.2.1)
- [x] Version bumped in src/index.ts
- [x] JSON parsing fix implemented in src/client.ts  
- [x] CHANGELOG.md updated
- [x] Build successful (`npm run build`)
- [x] Type checking passes (`npm run type-check`)
- [ ] Git changes committed and pushed
- [ ] Git tag created and pushed  
- [ ] NPM package published

---

Ready to release? Run `./release.sh` or follow the manual steps above! 🎉
