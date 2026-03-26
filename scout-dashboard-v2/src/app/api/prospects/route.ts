import { NextResponse } from 'next/server';
import { sql } from '@vercel/postgres';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const stage = searchParams.get('stage');
    const city = searchParams.get('city');
    const branch = searchParams.get('branch');

    let query = sql`SELECT * FROM prospects`;
    
    if (stage) {
      query = sql`SELECT * FROM prospects WHERE stage = ${stage}`;
    }
    if (city) {
      query = sql`SELECT * FROM prospects WHERE city = ${city}`;
    }
    if (branch) {
      query = sql`SELECT * FROM prospects WHERE branch = ${branch}`;
    }

    const result = await query;
    return NextResponse.json({ prospects: result.rows });
  } catch (error) {
    console.error('Prospects fetch error:', error);
    return NextResponse.json({ error: 'Failed to fetch prospects' }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { name, handle, followers, city, email, stage, type, branch, score } = body;

    const result = await sql`
      INSERT INTO prospects (name, handle, followers, city, email, stage, type, branch, score)
      VALUES (${name}, ${handle}, ${followers}, ${city}, ${email}, ${stage}, ${type}, ${branch}, ${score})
      RETURNING *
    `;

    return NextResponse.json({ prospect: result.rows[0] });
  } catch (error) {
    console.error('Prospect create error:', error);
    return NextResponse.json({ error: 'Failed to create prospect' }, { status: 500 });
  }
}
