const { Client } = require('pg');

const client = new Client({
  connectionString: "postgresql://postgres:JcZlzllYjv0BFgYV@db.jjjxkoxlbkrhixkbadva.supabase.co:5432/postgres",
  ssl: { rejectUnauthorized: false }
});

const initQueries = [
  `CREATE TABLE IF NOT EXISTS agent_status (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'unknown',
    "currentTask" TEXT,
    version TEXT DEFAULT '1.0.0',
    "lastHeartbeat" TIMESTAMP DEFAULT NOW(),
    "createdAt" TIMESTAMP DEFAULT NOW()
  )`,
  
  `CREATE TABLE IF NOT EXISTS activity_log (
    id SERIAL PRIMARY KEY,
    task TEXT NOT NULL,
    "createdAt" TIMESTAMP DEFAULT NOW()
  )`,
  
  `CREATE TABLE IF NOT EXISTS prospects (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name TEXT NOT NULL,
    handle TEXT NOT NULL,
    followers INTEGER DEFAULT 0,
    city TEXT NOT NULL,
    email TEXT,
    stage TEXT NOT NULL DEFAULT 'Uncontacted',
    type TEXT NOT NULL DEFAULT 'Nano',
    branch TEXT NOT NULL,
    score INTEGER DEFAULT 0,
    "draftStatus" TEXT,
    "lastContact" TIMESTAMP,
    "createdAt" TIMESTAMP DEFAULT NOW(),
    "updatedAt" TIMESTAMP DEFAULT NOW()
  )`,
  
  `CREATE TABLE IF NOT EXISTS drafts (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    "prospectId" TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    "createdAt" TIMESTAMP DEFAULT NOW(),
    "updatedAt" TIMESTAMP DEFAULT NOW()
  )`,
  
  `INSERT INTO agent_status (id, status, "currentTask", version)
   VALUES ('scout', 'idle', 'Dashboard initialized', '2.0.0')
   ON CONFLICT (id) DO NOTHING`
];

async function init() {
  await client.connect();
  console.log('Connected to Supabase');
  
  for (const query of initQueries) {
    try {
      await client.query(query);
      console.log('✅ Executed:', query.split('\n')[0].trim());
    } catch (e) {
      console.error('❌ Error:', e.message);
    }
  }
  
  await client.end();
  console.log('\n✅ Database initialized');
}

init().catch(console.error);
