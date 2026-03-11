import pg from 'pg';
const { Pool } = pg;

export function createPool(): InstanceType<typeof Pool> {
    const p = new Pool({
        host: process.env.PG_HOST || 'localhost',
        port: parseInt(process.env.PG_PORT || '5432'),
        database: process.env.PG_DATABASE || 'toolathlon',
        user: process.env.PG_USER || 'postgres',
        password: process.env.PG_PASSWORD || 'postgres',
        idleTimeoutMillis: 10000,
        connectionTimeoutMillis: 5000,
    });
    // Prevent unhandled error crashes on idle connection termination
    p.on('error', (_err, _client) => { /* swallow idle connection errors */ });
    return p;
}

export const pool = createPool();
