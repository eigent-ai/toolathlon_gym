# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Canvas MCP Server is a comprehensive Model Context Protocol (MCP) server that provides seamless integration with Canvas LMS. It offers 50+ tools covering student workflows, instructor functionality, and account administration.

The project is built as a TypeScript MCP server using the official MCP SDK, providing a bridge between Claude and Canvas LMS APIs.

## Architecture

### Core Components

- **`src/index.ts`** - Main MCP server entry point with 50+ tool definitions and request handlers
- **`src/client.ts`** - Canvas API client with comprehensive endpoint coverage, retry logic, and pagination handling
- **`src/types.ts`** - Complete TypeScript interfaces for all Canvas entities and tool arguments

### Key Design Patterns

- **MCP Server Pattern**: Uses `@modelcontextprotocol/sdk` for tool registration and request handling
- **Pagination Handling**: Automatic pagination via response interceptors for all Canvas list endpoints
- **Retry Logic**: Exponential backoff retry for rate limits and server errors
- **Resource-based API**: Exposes Canvas entities as MCP resources with dynamic URI schemes
- **Type Safety**: Comprehensive TypeScript interfaces with branded types for IDs

## Development Commands

### Essential Commands
```bash
# Build the project
npm run build

# Development with hot reload  
npm run dev:watch

# Run tests
npm run test

# Run specific test types
npm run test:unit
npm run test:integration

# Code quality checks
npm run lint
npm run type-check
npm run format:check

# Fix code formatting
npm run lint:fix
npm run format
```

### Docker Operations
```bash
# Build Docker image
npm run docker:build

# Run with Docker Compose
npm run docker:compose:up
npm run docker:compose:down
npm run docker:compose:logs
```

### Deployment & Release
```bash
# Health check
npm run health-check

# Release (runs build and type-check)
npm run release:dry-run
npm run release
```

## Canvas API Integration

### Authentication
The server requires two environment variables:
- `CANVAS_API_TOKEN` - Canvas API access token with appropriate scopes
- `CANVAS_DOMAIN` - Canvas instance domain (e.g., `school.instructure.com`)

### API Client Features
- **Automatic Pagination**: All list endpoints automatically fetch all pages
- **Retry Logic**: Exponential backoff for 429 (rate limit) and 5xx errors
- **Error Handling**: Structured error responses with proper Canvas API error parsing
- **Request Logging**: Comprehensive logging for debugging API interactions

### Tool Categories

**Student Tools (Core functionality)**:
- Course and assignment management
- Submission workflows (text, URL, file uploads)
- Grade tracking and dashboard access
- Discussion participation and messaging
- Module progress tracking
- Quiz taking and calendar events

**Instructor Tools**:
- Course creation with proper account association (fixed in v2.2.0)
- Assignment and quiz creation/management
- Grading workflows with rubric support
- User enrollment and management

**Account Admin Tools (v2.2.0+)**:
- Account-level course and user management
- User creation with pseudonym setup
- Report generation and analytics
- Sub-account management

## Development Guidelines

### When Adding New Tools

1. **Define TypeScript interfaces** in `src/types.ts` for all new Canvas entities and tool arguments
2. **Add client methods** in `src/client.ts` with proper error handling and typing
3. **Register tools** in the TOOLS array in `src/index.ts` with complete JSON schema
4. **Add request handlers** in the switch statement with validation and error handling
5. **Update tests** to cover new functionality

### Canvas API Patterns

- **Course Creation**: Always requires `account_id` parameter (critical fix in v2.2.0)
- **ID Parameters**: Use branded types for type safety (CourseId, AssignmentId, etc.)
- **Include Parameters**: Most endpoints support `include` arrays for related data
- **Pagination**: Client automatically handles pagination for all list endpoints
- **Error Responses**: Canvas returns various formats - client handles HTML, JSON, and text responses

### Testing Approach

The project uses Vitest for testing:
- **Unit tests**: Test individual client methods and utilities
- **Integration tests**: Test full tool workflows end-to-end
- **Coverage**: Generate coverage reports with `npm run coverage`

### Environment Configuration

The server loads environment variables from multiple locations:
- `.env` files in current directory, src/, and parent directories
- Standard environment variables
- Docker environment variable injection

### MCP Resource Pattern

Resources are exposed with URI schemes:
- `canvas://health` - API health status
- `course://{id}` - Individual course details
- `assignments://{course_id}` - Course assignments
- `modules://{course_id}` - Course modules
- `dashboard://user` - User dashboard

## Error Handling

The client implements comprehensive error handling:
- **Network errors**: Automatic retry with exponential backoff
- **Canvas API errors**: Proper parsing of various response formats (JSON, HTML, text)
- **Validation errors**: Input validation with descriptive messages
- **Rate limiting**: Automatic retry for 429 responses

## Key Changes in v2.2.0+

- **BREAKING**: Course creation now requires `account_id` parameter
- **NEW**: Complete account management functionality
- **NEW**: User creation and management tools
- **NEW**: Report generation capabilities
- **FIX**: Resolved "page not found" errors in course creation workflow