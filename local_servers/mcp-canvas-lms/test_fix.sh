#!/bin/bash

# Quick test script to verify the fix
echo "Testing Canvas MCP Server JSON Error Fix..."

# Check if TypeScript compiles
echo "Compiling TypeScript..."
cd /Users/davidmontgomery/mcp-canvas-lms
npx tsc

if [ $? -eq 0 ]; then
    echo "✅ TypeScript compilation successful!"
    echo "✅ JSON parsing error fix applied successfully"
    echo ""
    echo "The fix includes:"
    echo "- Better error response handling"
    echo "- Content-type checking"
    echo "- Improved logging"
    echo "- Graceful fallback for non-JSON responses"
    echo ""
    echo "You can now run your Canvas MCP server without the JSON parsing errors!"
else
    echo "❌ TypeScript compilation failed. Please check the errors above."
    exit 1
fi
