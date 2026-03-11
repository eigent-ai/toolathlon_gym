# Project Brief

## Core Requirements

*   Provide a set of tools to interact with the Google Forms API.
*   Enable programmatic creation of Google Forms.
*   Allow adding questions (text, multiple choice) to existing Google Forms.
*   Facilitate retrieval of form details and responses.
*   Operate as an MCP (Model Context Protocol) server.

## Goals

*   To simplify and automate interactions with Google Forms for users of an MCP-compatible client (e.g., Claude desktop app).
*   To provide a reliable and easy-to-configure server for Google Forms integration.
*   To handle Google API authentication securely using OAuth 2.0.

## Scope

*   **In Scope:**
    *   MCP server implementation using `@modelcontextprotocol/sdk`.
    *   Authentication with Google Forms API via OAuth 2.0 (Client ID, Client Secret, Refresh Token).
    *   A script (`get-refresh-token.ts`) to help users obtain a Google API refresh token.
    *   Tools:
        *   `create_form`: Create a new Google Form with a title and optional description.
        *   `add_text_question`: Add a text input question to a specified form.
        *   `add_multiple_choice_question`: Add a multiple-choice question with options to a specified form.
        *   `get_form`: Retrieve details of a specified form.
        *   `get_form_responses`: Retrieve responses submitted to a specified form.
*   **Out of Scope:**
    *   Direct user interface for managing forms (it's an API-driven server).
    *   Advanced form features beyond basic question types (e.g., file uploads, grids, sections, conditional logic).
    *   Managing form permissions or sharing settings.
    *   Real-time updates or push notifications for new responses.
    *   Storing form data or responses within the MCP server itself.

## Key Stakeholders

*   Users of MCP-compatible clients who need to interact with Google Forms.
*   Developers maintaining or extending this MCP server.

## Assumptions

*   Users have a Google account and can create a project in Google Cloud Console.
*   Users can enable the Google Forms API and obtain OAuth 2.0 credentials.
*   The MCP server will be run in an environment where Node.js is available.
*   Environment variables (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`) will be correctly set for the server to function.

## Constraints

*   Dependent on Google Forms API availability and its quotas/limitations.
*   Requires Node.js environment.
*   Authentication relies on OAuth 2.0 refresh tokens, which must be kept secure.
*   The server is designed to be run via an MCP client, not as a standalone web service.
