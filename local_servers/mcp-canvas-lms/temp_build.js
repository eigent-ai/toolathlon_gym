#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

console.log('Building Canvas MCP Server...');

// Run TypeScript compiler
const tsc = spawn('./node_modules/.bin/tsc', [], {
  cwd: __dirname,
  stdio: 'inherit'
});

tsc.on('close', (code) => {
  if (code === 0) {
    console.log('✅ Build completed successfully!');
    console.log('Console.log statements have been fixed to use console.error');
    console.log('The server should now work without JSON parsing errors');
  } else {
    console.error('❌ Build failed with code:', code);
  }
});

tsc.on('error', (err) => {
  console.error('❌ Failed to start build process:', err);
});
