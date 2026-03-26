import { NextResponse } from 'next/server';
import { sql } from '@vercel/postgres';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { status, currentTask, version = '1.0.0' } = body;

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

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Status update error:', error);
    return NextResponse.json({ error: 'Failed to update status' }, { status: 500 });
  }
}

export async function GET() {
  try {
    const result = await sql`
      SELECT * FROM agent_status WHERE id = 'scout'
    `;
    
    const activity = await sql`
      SELECT * FROM activity_log 
      ORDER BY "createdAt" DESC 
      LIMIT 10
    `;

    return NextResponse.json({
      status: result.rows[0] || null,
      activity: activity.rows
    });
  } catch (error) {
    console.error('Status fetch error:', error);
    return NextResponse.json({ error: 'Failed to fetch status' }, { status: 500 });
  }
}
