#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
    CallToolRequestSchema,
    ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema";
import pg from 'pg';

const { Pool } = pg;

// PostgreSQL connection pool
const pool = new Pool({
    host: process.env.PG_HOST || 'localhost',
    port: parseInt(process.env.PG_PORT || '5432'),
    database: process.env.PG_DATABASE || 'toolathlon',
    user: process.env.PG_USER || 'postgres',
    password: process.env.PG_PASSWORD || 'postgres',
});

// Helper to format a DB row into Google Calendar event JSON
function formatEvent(row: any) {
    return {
        id: row.id,
        summary: row.summary,
        description: row.description,
        location: row.location,
        start: {
            dateTime: row.start_datetime ? new Date(row.start_datetime).toISOString() : null,
            timeZone: row.start_timezone || undefined,
        },
        end: {
            dateTime: row.end_datetime ? new Date(row.end_datetime).toISOString() : null,
            timeZone: row.end_timezone || undefined,
        },
        status: row.status,
        htmlLink: row.html_link,
        creator: row.creator,
        organizer: row.organizer,
        attendees: row.attendees,
        recurrence: row.recurrence,
        reminders: row.reminders,
        created: row.created ? new Date(row.created).toISOString() : null,
        updated: row.updated ? new Date(row.updated).toISOString() : null,
    };
}

// PgCalendar class that mimics the google calendar.events.* interface
class PgCalendar {
    events: {
        insert: (params: { calendarId: string; requestBody: any }) => Promise<{ data: any }>;
        get: (params: { calendarId: string; eventId: string }) => Promise<{ data: any }>;
        patch: (params: { calendarId: string; eventId: string; requestBody: any }) => Promise<{ data: any }>;
        delete: (params: { calendarId: string; eventId: string }) => Promise<{ data: any }>;
        list: (params: { calendarId: string; timeMin?: string; timeMax?: string; maxResults?: number; orderBy?: string; singleEvents?: boolean }) => Promise<{ data: { items: any[] } }>;
    };

    constructor(pool: pg.Pool) {
        const self = this;

        this.events = {
            async insert({ calendarId, requestBody }: { calendarId: string; requestBody: any }) {
                const startDateTime = requestBody.start?.dateTime;
                const startTimeZone = requestBody.start?.timeZone || null;
                const endDateTime = requestBody.end?.dateTime;
                const endTimeZone = requestBody.end?.timeZone || null;
                const result = await pool.query(
                    `INSERT INTO gcal.events (summary, description, location, start_datetime, start_timezone, end_datetime, end_timezone)
                     VALUES ($1, $2, $3, $4, $5, $6, $7)
                     RETURNING *`,
                    [
                        requestBody.summary || null,
                        requestBody.description || null,
                        requestBody.location || null,
                        startDateTime,
                        startTimeZone,
                        endDateTime,
                        endTimeZone,
                    ]
                );
                return { data: formatEvent(result.rows[0]) };
            },

            async get({ calendarId, eventId }: { calendarId: string; eventId: string }) {
                const result = await pool.query(
                    `SELECT * FROM gcal.events WHERE id = $1`,
                    [eventId]
                );
                if (result.rows.length === 0) {
                    throw new Error(`Event not found: ${eventId}`);
                }
                return { data: formatEvent(result.rows[0]) };
            },

            async patch({ calendarId, eventId, requestBody }: { calendarId: string; eventId: string; requestBody: any }) {
                const setClauses: string[] = [];
                const values: any[] = [];
                let paramIndex = 1;

                if (requestBody.summary !== undefined) {
                    setClauses.push(`summary = $${paramIndex++}`);
                    values.push(requestBody.summary);
                }
                if (requestBody.description !== undefined) {
                    setClauses.push(`description = $${paramIndex++}`);
                    values.push(requestBody.description);
                }
                if (requestBody.location !== undefined) {
                    setClauses.push(`location = $${paramIndex++}`);
                    values.push(requestBody.location);
                }
                if (requestBody.start?.dateTime !== undefined) {
                    setClauses.push(`start_datetime = $${paramIndex++}`);
                    values.push(requestBody.start.dateTime);
                }
                if (requestBody.start?.timeZone !== undefined) {
                    setClauses.push(`start_timezone = $${paramIndex++}`);
                    values.push(requestBody.start.timeZone);
                }
                if (requestBody.end?.dateTime !== undefined) {
                    setClauses.push(`end_datetime = $${paramIndex++}`);
                    values.push(requestBody.end.dateTime);
                }
                if (requestBody.end?.timeZone !== undefined) {
                    setClauses.push(`end_timezone = $${paramIndex++}`);
                    values.push(requestBody.end.timeZone);
                }

                // Always update the updated timestamp
                setClauses.push(`updated = NOW()`);

                if (setClauses.length === 1) {
                    // Only the updated timestamp, no real changes; just fetch
                    const result = await pool.query(`SELECT * FROM gcal.events WHERE id = $1`, [eventId]);
                    if (result.rows.length === 0) throw new Error(`Event not found: ${eventId}`);
                    return { data: formatEvent(result.rows[0]) };
                }

                values.push(eventId);
                const result = await pool.query(
                    `UPDATE gcal.events SET ${setClauses.join(', ')} WHERE id = $${paramIndex} RETURNING *`,
                    values
                );
                if (result.rows.length === 0) {
                    throw new Error(`Event not found: ${eventId}`);
                }
                return { data: formatEvent(result.rows[0]) };
            },

            async delete({ calendarId, eventId }: { calendarId: string; eventId: string }) {
                const result = await pool.query(
                    `DELETE FROM gcal.events WHERE id = $1`,
                    [eventId]
                );
                if (result.rowCount === 0) {
                    throw new Error(`Event not found: ${eventId}`);
                }
                return { data: {} };
            },

            async list({ calendarId, timeMin, timeMax, maxResults, orderBy, singleEvents }: {
                calendarId: string;
                timeMin?: string;
                timeMax?: string;
                maxResults?: number;
                orderBy?: string;
                singleEvents?: boolean;
            }) {
                const conditions: string[] = [];
                const values: any[] = [];
                let paramIndex = 1;

                if (timeMin) {
                    conditions.push(`start_datetime >= $${paramIndex++}`);
                    values.push(timeMin);
                }
                if (timeMax) {
                    conditions.push(`end_datetime <= $${paramIndex++}`);
                    values.push(timeMax);
                }

                const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

                let orderClause = 'ORDER BY start_datetime ASC';
                if (orderBy === 'updated') {
                    orderClause = 'ORDER BY updated DESC';
                }

                const limitClause = maxResults ? `LIMIT $${paramIndex++}` : '';
                if (maxResults) {
                    values.push(maxResults);
                }

                const result = await pool.query(
                    `SELECT * FROM gcal.events ${whereClause} ${orderClause} ${limitClause}`,
                    values
                );

                return { data: { items: result.rows.map(formatEvent) } };
            },
        };
    }
}

// Schema definitions
const CreateEventSchema = z.object({
    summary: z.string().describe("Event title"),
    start: z.object({
        dateTime: z.string().describe("Start time (ISO format)"),
        timeZone: z.string().optional().describe("Time zone"),
    }),
    end: z.object({
        dateTime: z.string().describe("End time (ISO format)"),
        timeZone: z.string().optional().describe("Time zone"),
    }),
    description: z.string().optional().describe("Event description"),
    location: z.string().optional().describe("Event location"),
});

const GetEventSchema = z.object({
    eventId: z.string().describe("ID of the event to retrieve"),
});

const UpdateEventSchema = z.object({
    eventId: z.string().describe("ID of the event to update"),
    summary: z.string().optional().describe("New event title"),
    start: z.object({
        dateTime: z.string().describe("New start time (ISO format)"),
        timeZone: z.string().optional().describe("Time zone"),
    }).optional(),
    end: z.object({
        dateTime: z.string().describe("New end time (ISO format)"),
        timeZone: z.string().optional().describe("Time zone"),
    }).optional(),
    description: z.string().optional().describe("New event description"),
    location: z.string().optional().describe("New event location"),
});

const DeleteEventSchema = z.object({
    eventId: z.string().describe("ID of the event to delete"),
});

const ListEventsSchema = z.object({
    timeMin: z.string().describe("Start of time range (ISO format)"),
    timeMax: z.string().describe("End of time range (ISO format)"),
    maxResults: z.number().optional().describe("Maximum number of events to return"),
    orderBy: z.enum(['startTime', 'updated']).optional().describe("Sort order"),
});

// Main function
async function main() {
    // Initialize PgCalendar
    const calendar = new PgCalendar(pool);
    const calendarId = 'primary';

    // Server implementation
    const server = new Server({
        name: "google-calendar",
        version: "1.0.0",
        capabilities: {
            tools: {},
        },
    });

    // Tool handlers
    server.setRequestHandler(ListToolsRequestSchema, async () => ({
        tools: [
            {
                name: "create_event",
                description: "Creates a new event in Google Calendar",
                inputSchema: zodToJsonSchema(CreateEventSchema),
            },
            {
                name: "get_event",
                description: "Retrieves details of a specific event",
                inputSchema: zodToJsonSchema(GetEventSchema),
            },
            {
                name: "update_event",
                description: "Updates an existing event",
                inputSchema: zodToJsonSchema(UpdateEventSchema),
            },
            {
                name: "delete_event",
                description: "Deletes an event from the calendar",
                inputSchema: zodToJsonSchema(DeleteEventSchema),
            },
            {
                name: "list_events",
                description: "Lists events within a specified time range",
                inputSchema: zodToJsonSchema(ListEventsSchema),
            },
        ],
    }));

    server.setRequestHandler(CallToolRequestSchema, async (request) => {
        const { name, arguments: args } = request.params;

        try {
            switch (name) {
                case "create_event": {
                    const validatedArgs = CreateEventSchema.parse(args);
                    const response = await calendar.events.insert({
                        calendarId,
                        requestBody: validatedArgs,
                    });
                    return {
                        content: [
                            {
                                type: "text",
                                text: `Event created with ID: ${response.data.id}\n` +
                                      `Title: ${validatedArgs.summary}\n` +
                                      `Start: ${validatedArgs.start.dateTime}\n` +
                                      `End: ${validatedArgs.end.dateTime}`,
                            },
                        ],
                    };
                }

                case "get_event": {
                    const validatedArgs = GetEventSchema.parse(args);
                    const response = await calendar.events.get({
                        calendarId,
                        eventId: validatedArgs.eventId,
                    });
                    return {
                        content: [
                            {
                                type: "text",
                                text: JSON.stringify(response.data, null, 2),
                            },
                        ],
                    };
                }

                case "update_event": {
                    const validatedArgs = UpdateEventSchema.parse(args);
                    const { eventId, ...updates } = validatedArgs;
                    const response = await calendar.events.patch({
                        calendarId,
                        eventId,
                        requestBody: updates,
                    });
                    return {
                        content: [
                            {
                                type: "text",
                                text: `Event updated: ${eventId}\n` +
                                      `New title: ${updates.summary || '(unchanged)'}\n` +
                                      `New start: ${updates.start?.dateTime || '(unchanged)'}\n` +
                                      `New end: ${updates.end?.dateTime || '(unchanged)'}`,
                            },
                        ],
                    };
                }

                case "delete_event": {
                    const validatedArgs = DeleteEventSchema.parse(args);
                    await calendar.events.delete({
                        calendarId,
                        eventId: validatedArgs.eventId,
                    });
                    return {
                        content: [
                            {
                                type: "text",
                                text: `Event deleted: ${validatedArgs.eventId}`,
                            },
                        ],
                    };
                }

                case "list_events": {
                    const validatedArgs = ListEventsSchema.parse(args);
                    const response = await calendar.events.list({
                        calendarId,
                        timeMin: validatedArgs.timeMin,
                        timeMax: validatedArgs.timeMax,
                        maxResults: validatedArgs.maxResults || 10,
                        orderBy: validatedArgs.orderBy || 'startTime',
                        singleEvents: true,
                    });
                    return {
                        content: [
                            {
                                type: "text",
                                text: `Found ${response.data.items?.length || 0} events:\n` +
                                      JSON.stringify(response.data.items, null, 2),
                            },
                        ],
                    };
                }

                default:
                    throw new Error(`Unknown tool: ${name}`);
            }
        } catch (error) {
            return {
                content: [
                    {
                        type: "text",
                        text: `Error: ${error instanceof Error ? error.message : String(error)}`,
                    },
                ],
                isError: true,
            };
        }
    });

    // Start the server
    const transport = new StdioServerTransport();
    server.connect(transport).catch((error) => {
        console.error("Fatal error running server:", error);
        process.exit(1);
    });
    console.error('Google Calendar MCP Server running on stdio');
}

main().catch(console.error);
