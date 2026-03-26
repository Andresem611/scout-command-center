import { NextResponse } from 'next/server';
import { createClient } from '@vercel/postgres';

// Initialize tables if they don't exist
async function initTables(sql: any) {
  try {
    await sql`CREATE TABLE IF NOT EXISTS agent_status (
      id TEXT PRIMARY KEY,
      status TEXT NOT NULL DEFAULT 'unknown',
      "currentTask" TEXT,
      version TEXT DEFAULT '1.0.0',
      "lastHeartbeat" TIMESTAMP DEFAULT NOW(),
      "createdAt" TIMESTAMP DEFAULT NOW()
    )`;
    await sql`CREATE TABLE IF NOT EXISTS activity_log (
      id SERIAL PRIMARY KEY,
      task TEXT NOT NULL,
      "createdAt" TIMESTAMP DEFAULT NOW()
    )`;
    await sql`INSERT INTO agent_status (id, status, "currentTask", version)
      VALUES ('scout', 'idle', 'Dashboard initialized', '2.0.0')
      ON CONFLICT (id) DO NOTHING`;
  } catch (e) {
    console.log('Init error (may already exist):', e);
  }
}

export async function POST(request: Request) {
  const client = createClient();
  await client.connect();
  const sql = client.sql.bind(client);
  try {
    const body = await request.json();
    const { status, currentTask, version = '1.0.0' } = body;

    await initTables(sql);

    // Upsert agent status
    await sql`
      INSERT INTO agent_status (id, status, "currentTask", version, "lastHeartbeat")
      VALUES ('scout', ${status}, ${currentTask}, ${version}, NOW())
      ON CONFLICT (id) 
      DO UPDATE SET 
        status = ${status},
        "currentTask" = ${currentTask},
        version = ${version},
        "lastHeartbeat" = NOW()
    `;

    // Log activity
    if (currentTask) {
      await sql`
        INSERT INTO activity_log (task, "createdAt")
        VALUES (${currentTask}, NOW())
      `;
    }

    await client.end();
    return NextResponse.json({ success: true });
  } catch (error) {
    await client.end();
    console.error('Status update error:', error);
    return NextResponse.json({ error: 'Failed to update status' }, { status: 500 });
  }
}

export async function GET() {
  const client = createClient();
  await client.connect();
  const sql = client.sql.bind(client);
  
  try {
    await initTables(sql);
    
    const result = await sql`
      SELECT * FROM agent_status WHERE id = 'scout'
    `;
    
    const activity = await sql`
      SELECT * FROM activity_log 
      ORDER BY "createdAt" DESC 
      LIMIT 10
    `;

    await client.end();
    return NextResponse.json({
      status: result.rows[0] || null,
      activity: activity.rows
    });
  } catch (error) {
    await client.end();
    console.error('Status fetch error:', error);
    return NextResponse.json({ error: 'Failed to fetch status' }, { status: 500 });
  }
}
