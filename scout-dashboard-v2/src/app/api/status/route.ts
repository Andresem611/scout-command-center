import { NextResponse } from 'next/server';
import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

const DATA_FILE = join(process.cwd(), '..', 'scout_data.json');

function loadData() {
  try {
    const content = readFileSync(DATA_FILE, 'utf-8');
    return JSON.parse(content);
  } catch (error) {
    console.error('Failed to load scout_data.json:', error);
    return { prospects: [], stats: {}, agent_status: {} };
  }
}

function saveData(data: any) {
  try {
    writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
  } catch (error) {
    console.error('Failed to save scout_data.json:', error);
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { status, currentTask, version = '2.0.0' } = body;

    const data = loadData();
    
    // Update agent status
    if (!data.agent_status) {
      data.agent_status = {};
    }
    
    data.agent_status.status = status;
    data.agent_status.currentTask = currentTask;
    data.agent_status.version = version;
    data.agent_status.lastHeartbeat = new Date().toISOString();
    
    // Add to activity log
    if (!data.agent_status.activity_log) {
      data.agent_status.activity_log = [];
    }
    
    if (currentTask) {
      data.agent_status.activity_log.unshift({
        task: currentTask,
        time: new Date().toISOString()
      });
      // Keep last 50
      data.agent_status.activity_log = data.agent_status.activity_log.slice(0, 50);
    }

    saveData(data);
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Status update error:', error);
    return NextResponse.json({ error: 'Failed to update status' }, { status: 500 });
  }
}

export async function GET() {
  try {
    const data = loadData();
    const agentStatus = data.agent_status || {};
    
    // Transform activity log format
    const activity = (agentStatus.activity_log || []).map((item: any) => ({
      task: item.task,
      createdAt: item.time
    }));

    return NextResponse.json({
      status: {
        id: 'scout',
        status: agentStatus.status || 'idle',
        currentTask: agentStatus.currentTask || 'Waiting for heartbeat',
        version: agentStatus.version || '2.0.0',
        lastHeartbeat: agentStatus.lastHeartbeat || null
      },
      activity
    });
  } catch (error) {
    console.error('Status fetch error:', error);
    return NextResponse.json({ error: 'Failed to fetch status' }, { status: 500 });
  }
}
