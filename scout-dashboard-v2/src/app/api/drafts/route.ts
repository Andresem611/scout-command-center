import { NextResponse } from 'next/server';
import { sql } from '@vercel/postgres';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { prospectId, subject, body: emailBody } = body;

    // Create draft
    const draft = await sql`
      INSERT INTO drafts ("prospectId", subject, body, status)
      VALUES (${prospectId}, ${subject}, ${emailBody}, 'pending')
      RETURNING *
    `;

    // Update prospect draft status
    await sql`
      UPDATE prospects 
      SET "draftStatus" = 'pending', "updatedAt" = NOW()
      WHERE id = ${prospectId}
    `;

    return NextResponse.json({ draft: draft.rows[0] });
  } catch (error) {
    console.error('Draft create error:', error);
    return NextResponse.json({ error: 'Failed to create draft' }, { status: 500 });
  }
}

export async function PATCH(request: Request) {
  try {
    const body = await request.json();
    const { id, status } = body;

    const result = await sql`
      UPDATE drafts 
      SET status = ${status}, "updatedAt" = NOW()
      WHERE id = ${id}
      RETURNING *
    `;

    if (result.rows[0]) {
      await sql`
        UPDATE prospects 
        SET "draftStatus" = ${status}, "updatedAt" = NOW()
        WHERE id = ${result.rows[0].prospectId}
      `;
    }

    return NextResponse.json({ draft: result.rows[0] });
  } catch (error) {
    console.error('Draft update error:', error);
    return NextResponse.json({ error: 'Failed to update draft' }, { status: 500 });
  }
}
