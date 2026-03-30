"use client";

import { useEffect, useState } from "react";

interface BranchTarget {
  name: string;
  target: number;
  current: number;
  cities: string;
}

interface AgentStatus {
  status: string;
  currentTask: string;
  lastHeartbeat: string;
  version: string;
}

interface ActivityItem {
  task: string;
  createdAt: string;
}

interface Stats {
  total: number;
  contacted: number;
  replied: number;
  activePartners: number;
}

// Updated to match actual data structure from scout_data.json
const BRANCH_TARGETS: BranchTarget[] = [
  { name: "Mom Influencers", target: 95, current: 0, cities: "NYC, Miami, LA, SF, Houston, Dallas, Austin, Chicago" },
  { name: "Mom Blog", target: 15, current: 0, cities: "Same cities" },
  { name: "Homeschool", target: 35, current: 0, cities: "AZ, FL, UT, TX" },
];

const EMAIL_TEMPLATE = `Hi [name],

This is Keri! I'm a pianist, music teacher, and co-founder of Thoven — an all-in-one music education platform where families can find verified, background-checked teachers trained at top schools like The Juilliard School and book lessons easily, anytime, anywhere.

After years of teaching and working closely with families, I've met so many parents who wanted music lessons for their children but feel unsure where to begin or how to stay connected to their child's progress. That's why we built Thoven.

With Thoven, parents and students can:
• Feel confident knowing every teacher is background-checked and verified
• Seamlessly schedule and pay for lessons in one place (secured with Stripe)
• Access a personalized, gamified dashboard to track progress and motivate practice
• View lesson notes, assignments, and real-time progress updates

We work with a growing group of teachers trained at The Juilliard School, Manhattan School of Music, Eastman School of Music and more.

I love the way your content connects with your audience, so I wanted to reach out personally to see if you'd be open to working together in a way that feels natural for you and your audience.

We'd be happy to structure this in a way that works best for you:
• Affiliate partnership: Earn commission on every lesson booked through your unique link
• Complimentary lessons: We can provide free lessons to your family so you can experience the platform and see the value firsthand
• Other approaches: If you have a preferred method or different structure in mind, we're open to exploring options that work best for you

If you're interested, I'd love to schedule a quick call to walk you through the platform, answer any questions, and explore what a partnership could look like.

If you'd like to learn more, you can find us at Thoven in the meantime —

Looking forward to connecting!

Keri Erten
Co-Founder & CXO
Music Educator & Pianist`;

function StatCard({ title, value, subtitle, color }: { title: string; value: string; subtitle: string; color: string }) {
  const colorClasses: Record<string, string> = {
    green: "text-green-400",
    blue: "text-blue-400",
    yellow: "text-yellow-400",
    purple: "text-purple-400",
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 text-center">
      <p className="text-sm text-gray-500 mb-2">{title}</p>
      <p className={`text-4xl font-bold ${colorClasses[color]} mb-1`}>{value}</p>
      <p className="text-sm text-gray-600">{subtitle}</p>
    </div>
  );
}

function BranchProgress({ branch }: { branch: BranchTarget }) {
  const percentage = Math.min(100, Math.round((branch.current / branch.target) * 100));
  
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
      <div className="flex items-center justify-between mb-2">
        <div>
          <h3 className="font-medium">{branch.name}</h3>
          <p className="text-xs text-gray-500">{branch.cities}</p>
        </div>
        <span className={`text-sm font-medium ${percentage >= 100 ? 'text-green-400' : percentage >= 50 ? 'text-yellow-400' : 'text-gray-400'}`}>
          {branch.current} / {branch.target}
        </span>
      </div>
      <div className="w-full bg-gray-800 rounded-full h-2">
        <div 
          className={`h-2 rounded-full transition-all ${percentage >= 100 ? 'bg-green-500' : percentage >= 50 ? 'bg-yellow-500' : 'bg-blue-500'}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null);
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [stats, setStats] = useState<Stats>({ total: 0, contacted: 0, replied: 0, activePartners: 1 });
  const [branches, setBranches] = useState<BranchTarget[]>(BRANCH_TARGETS);
  const [loading, setLoading] = useState(true);
  const [showTemplate, setShowTemplate] = useState(false);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  async function fetchData() {
    try {
      const [statusRes, prospectsRes] = await Promise.all([
        fetch("/api/status"),
        fetch("/api/prospects"),
      ]);

      const statusData = await statusRes.json();
      setAgentStatus(statusData.status);
      setActivity(statusData.activity || []);

      const prospectsData = await prospectsRes.json();
      const prospects = prospectsData.prospects || [];
      
      const contacted = prospects.filter((p: any) => p.stage === 'Contacted').length;
      const replied = prospects.filter((p: any) => ['Replied', 'Negotiating'].includes(p.stage)).length;
      
      setStats({
        total: prospects.length,
        contacted,
        replied,
        activePartners: prospects.filter((p: any) => p.stage === 'Partner').length || 1
      });

      // Update branch counts - match exact branch names from data
      const branchCounts: Record<string, number> = {};
      prospects.forEach((p: any) => {
        const branch = p.branch || 'Unknown';
        branchCounts[branch] = (branchCounts[branch] || 0) + 1;
      });

      const updatedBranches = BRANCH_TARGETS.map(branch => ({
        ...branch,
        current: branchCounts[branch.name] || 0
      }));
      setBranches(updatedBranches);
    } catch (error) {
      console.error("Failed to fetch data:", error);
    } finally {
      setLoading(false);
    }
  }

  function getStatusColor(status: string) {
    switch (status) {
      case "active": return "text-green-400 border-green-400";
      case "idle": return "text-yellow-400 border-yellow-400";
      case "error": return "text-red-400 border-red-400";
      default: return "text-gray-400 border-gray-400";
    }
  }

  function getStatusDot(status: string) {
    switch (status) {
      case "active": return "🟢";
      case "idle": return "🟡";
      case "error": return "🔴";
      default: return "⚪";
    }
  }

  function timeSince(dateString: string) {
    if (!dateString) return "—";
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    if (seconds < 60) return "Just now";
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading Scout Command Center...</div>
      </div>
    );
  }

  const borderColor = agentStatus ? getStatusColor(agentStatus.status).split(" ")[1] : "border-gray-600";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Scout Command Center</h1>
        <span className="text-xs text-gray-600">v2.0.0</span>
      </div>

      {/* Agent Status */}
      <div className={`bg-gray-900 border border-gray-800 rounded-xl p-6 border-l-4 ${borderColor}`}>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <span>🤖 Scout Agent</span>
              <span>{agentStatus ? getStatusDot(agentStatus.status) : "⚪"}</span>
            </h2>
            <p className="text-gray-400 mt-1">
              Last seen:{" "}
              <span className={agentStatus ? getStatusColor(agentStatus.status).split(" ")[0] : "text-gray-400"}>
                {agentStatus?.lastHeartbeat ? timeSince(agentStatus.lastHeartbeat) : "—"}
              </span>
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Current Task</p>
            <p className="text-lg font-medium">{agentStatus?.currentTask || "Waiting for heartbeat"}</p>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard title="Total Pipeline" value={stats.total.toString()} subtitle="of 145 target" color="green" />
        <StatCard title="Contacted" value={stats.contacted.toString()} subtitle="outreach sent" color="blue" />
        <StatCard title="Reply Rate" value={stats.contacted > 0 ? `${Math.round((stats.replied / stats.contacted) * 100)}%` : "0%"} subtitle={`${stats.replied} replies`} color="yellow" />
        <StatCard title="Active Partners" value={stats.activePartners.toString()} subtitle={stats.activePartners > 1 ? "Multiple partners" : "Audrey Mora"} color="purple" />
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Branch Progress */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">📊 Branch Progress</h3>
          <div className="space-y-3">
            {branches.map((branch, i) => (
              <BranchProgress key={i} branch={branch} />
            ))}
          </div>
        </div>

        {/* Email Template */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">📧 Email Template</h3>
            <button
              onClick={() => setShowTemplate(!showTemplate)}
              className="text-sm text-blue-400 hover:text-blue-300"
            >
              {showTemplate ? "Hide" : "Show"}
            </button>
          </div>
          {showTemplate ? (
            <pre className="text-xs text-gray-300 whitespace-pre-wrap bg-gray-950 p-4 rounded-lg overflow-y-auto max-h-96 font-mono">
              {EMAIL_TEMPLATE}
            </pre>
          ) : (
            <p className="text-gray-500 text-sm">Template hidden. Click Show to view the full outreach template.</p>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4">📜 Recent Activity</h3>
        {activity.length > 0 ? (
          <div className="space-y-2">
            {activity.slice(0, 10).map((item, i) => (
              <div key={i} className="flex items-center gap-3 text-sm py-2 border-b border-gray-800 last:border-0">
                <span className="text-gray-500 w-16">
                  {new Date(item.createdAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </span>
                <span>{item.task}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No recent activity</p>
        )}
      </div>
    </div>
  );
}
