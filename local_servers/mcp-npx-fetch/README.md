# MCP NPX Fetch

<div align="center">

[![npm version](https://img.shields.io/npm/v/@tokenizin/mcp-npx-fetch.svg)](https://www.npmjs.com/package/@tokenizin/mcp-npx-fetch)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-blue.svg)](https://www.typescriptlang.org/)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://github.com/modelcontextprotocol)

A powerful MCP server for fetching and transforming web content into various formats (HTML, JSON, Markdown, Plain Text) with ease.

[Installation](#installation) •
[Features](#features) •
[Usage](#usage) •
[Documentation](#documentation) •
[Contributing](#contributing)

</div>

<a href="https://glama.ai/mcp/servers/m2a0ue08n2"><img width="380" height="200" src="https://glama.ai/mcp/servers/m2a0ue08n2/badge" alt="NPX Fetch MCP server" /></a>

---

## 🚀 Features

- 🌐 **Universal Content Fetching**: Supports HTML, JSON, plain text, and Markdown formats
- 🔒 **Custom Headers Support**: Add authentication and custom headers to your requests
- 🛠 **Built-in Transformations**: Automatic conversion between formats
- ⚡ **High Performance**: Built with modern JavaScript features and optimized for speed
- 🔌 **MCP Compatible**: Seamlessly integrates with Claude Desktop and other MCP clients
- 🎯 **Type-Safe**: Written in TypeScript with full type definitions

## 📦 Installation

### NPM Global Installation

```bash
npm install -g @tokenizin/mcp-npx-fetch

```

### Direct Usage with NPX

```bash
npx @tokenizin/mcp-npx-fetch
```

## 📚 Documentation

### Available Tools

#### `fetch_html`

Fetches and returns raw HTML content from any URL.

```typescript
{
  url: string;     // Required: Target URL
  headers?: {      // Optional: Custom request headers
    [key: string]: string;
  };
}
```

#### `fetch_json`

Fetches and parses JSON data from any URL.

```typescript
{
  url: string;     // Required: Target URL
  headers?: {      // Optional: Custom request headers
    [key: string]: string;
  };
}
```

#### `fetch_txt`

Fetches and returns clean plain text content, removing HTML tags and scripts.

```typescript
{
  url: string;     // Required: Target URL
  headers?: {      // Optional: Custom request headers
    [key: string]: string;
  };
}
```

#### `fetch_markdown`

Fetches content and converts it to well-formatted Markdown.

```typescript
{
  url: string;     // Required: Target URL
  headers?: {      // Optional: Custom request headers
    [key: string]: string;
  };
}
```

## 🔧 Usage

### CLI Usage

Start the MCP server directly:

```bash
mcp-npx-fetch
```

Or via npx:

```bash
npx @tokenizin/mcp-npx-fetch
```

### Claude Desktop Integration

1. Locate your Claude Desktop configuration file:

   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Add the following configuration to your `mcpServers` object:

```json
{
  "mcpServers": {
    "fetch": {
      "command": "npx",
      "args": ["-y", "@tokenizin/mcp-npx-fetch"],
      "env": {}
    }
  }
}
```

## 💻 Local Development

1. Clone the repository:

```bash
git clone https://github.com/tokenizin-agency/mcp-npx-fetch.git
cd mcp-npx-fetch
```

2. Install dependencies:

```bash
npm install
```

3. Start development mode:

```bash
npm run dev
```

4. Run tests:

```bash
npm test
```

## 🛠 Technical Stack

- [Model Context Protocol SDK](https://github.com/modelcontextprotocol/sdk) - Core MCP functionality
- [JSDOM](https://github.com/jsdom/jsdom) - HTML parsing and manipulation
- [Turndown](https://github.com/mixmark-io/turndown) - HTML to Markdown conversion
- [TypeScript](https://www.typescriptlang.org/) - Type safety and modern JavaScript features
- [Zod](https://github.com/colinhacks/zod) - Runtime type validation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
Made with ❤️ by <a href="https://github.com/tokenizin-agency">PT Tokenizin Technology Agency</a>
</div>
