# Canvas MCP Server v2.2.2 - Release Commands

## Quick Deploy (Automated)
```bash
cd /Users/davidmontgomery/mcp-canvas-lms
chmod +x deploy-fix.sh
./deploy-fix.sh
```

## Manual Step-by-Step (if you prefer control)

### 1. Build the project
```bash
cd /Users/davidmontgomery/mcp-canvas-lms
npm run clean
npm run build
```

### 2. Git operations
```bash
# Add all changes
git add .

# Check what's being committed
git status

# Commit with descriptive message
git commit -m "fix: resolve console.log stdout pollution causing JSON parsing errors

- Changed console.log to console.error in src/client.ts (request logging, error responses, retries)
- Fixed tool execution logging in src/index.ts to use stderr  
- Eliminates 'Unexpected token C, [Canvas API' JSON parsing errors
- MCP protocol now receives clean JSON communication over stdio
- Version bump to 2.2.2

Fixes JSON parsing error spam in Claude Desktop"

# Force push to main (be careful!)
git push origin main --force
```

### 3. Publish to npm
```bash
# Publish the new version
npm publish
```

## What this fixes:
✅ Eliminates the constant "Unexpected token 'C', '[Canvas API'..." errors  
✅ Stops the 10 errors/second JSON parsing spam in Claude Desktop  
✅ Makes MCP communication clean (JSON only on stdout, logs on stderr)  
✅ No breaking changes - purely a protocol fix  

## Version Changes:
- 2.2.1 → 2.2.2 (patch version for the console.log fix)
- Updated in both package.json and src/index.ts
- Added comprehensive CHANGELOG entry

The core issue was debug logs polluting stdout which broke MCP's JSON communication protocol!
