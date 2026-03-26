import { NextResponse } from 'next/server';
import { readFileSync } from 'fs';
import { join } from 'path';

const DATA_FILE = join(process.cwd(), '..', 'scout_data.json');

function loadData() {
  try {
    const content = readFileSync(DATA_FILE, 'utf-8');
    return JSON.parse(content);
  } catch (error) {
    console.error('Failed to load scout_data.json:', error);
    return { prospects: [], stats: {} };
  }
}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const stage = searchParams.get('stage');
    const city = searchParams.get('city');
    const branch = searchParams.get('branch');

    const data = loadData();
    let prospects = data.prospects || [];

    if (stage) {
      prospects = prospects.filter((p: any) => p.stage === stage);
    }
    if (city) {
      prospects = prospects.filter((p: any) => p.city === city);
    }
    if (branch) {
      prospects = prospects.filter((p: any) => p.branch === branch);
    }

    return NextResponse.json({ prospects, count: prospects.length });
  } catch (error) {
    console.error('Prospects fetch error:', error);
    return NextResponse.json({ error: 'Failed to fetch prospects' }, { status: 500 });
  }
}
