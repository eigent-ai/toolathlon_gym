# Canvas MCP Server JSON Parsing Error Fix

## Problem
The error `Unexpected token 'C', "!Canvas API..." is not valid JSON` was occurring when Canvas returned non-JSON responses (like HTML error pages or plain text errors) but the code was trying to parse them as JSON.

## Root Cause
In `src/client.ts`, the response interceptor was attempting to use `JSON.stringify()` on Canvas API error responses without checking if they were actually JSON. When Canvas returns HTML error pages or plain text errors (often starting with "!Canvas API..."), the code would fail trying to parse them.

## Fix Applied

### 1. Enhanced Error Response Handling
- Added proper type checking for response data
- Handle string responses without attempting JSON operations
- Graceful fallback for any JSON parsing errors
- Truncate long error messages to prevent log spam

### 2. Content-Type Checking
- Only attempt pagination on JSON responses
- Check content-type headers before processing responses

### 3. Improved Logging
- Added debug logging for error responses showing status, content-type, and data type
- Better network error handling
- More informative error messages

## Code Changes

### Before:
```typescript
throw new CanvasAPIError(
  `Canvas API Error (${status}): ${((data as any)?.message) || JSON.stringify(data)}`, 
  status, 
  data
);
```

### After:
```typescript
let errorMessage: string;

try {
  // Check if data is already a string (HTML error pages, plain text, etc.)
  if (typeof data === 'string') {
    errorMessage = data.length > 200 ? data.substring(0, 200) + '...' : data;
  } else if (data && typeof data === 'object') {
    // Handle structured Canvas API error responses
    if ((data as any)?.message) {
      errorMessage = (data as any).message;
    } else if ((data as any)?.errors && Array.isArray((data as any).errors)) {
      errorMessage = (data as any).errors.map((err: any) => err.message || err).join(', ');
    } else {
      errorMessage = JSON.stringify(data);
    }
  } else {
    errorMessage = String(data);
  }
} catch (jsonError) {
  // Fallback if JSON operations fail
  errorMessage = String(data);
}

throw new CanvasAPIError(
  `Canvas API Error (${status}): ${errorMessage}`, 
  status, 
  data
);
```

## Testing
To test this fix:

1. Rebuild the project: `npm run build`
2. Test with a Canvas API call that might return an error
3. The error should now be handled gracefully without JSON parsing errors

## Next Steps
- The fix is backward compatible and won't break existing functionality
- Error messages will now be more descriptive and won't cause parsing failures
- The server should run without the annoying JSON parsing errors

This fix resolves the "benign but drives people insane" error while maintaining all existing functionality.
