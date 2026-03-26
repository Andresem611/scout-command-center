"use client";

import { useEffect, useState } from "react";

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

interface StatCardProps {
  title: string;
  value: string;
  subtitle: string;
  color: string;
}

function StatCard({ title, value, subtitle, color }: StatCardProps) {
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

export default function Dashboard() {
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null);
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [stats, setStats] = useState<Stats>({ total: 0, contacted: 0, replied: 0, activePartners: 1 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  async function fetchData() {
    try {
      // Fetch agent status
      const statusRes = await fetch("/api/status");
      const statusData = await statusRes.json();
      setAgentStatus(statusData.status);
      setActivity(statusData.activity || []);

      // Fetch prospects stats
      const prospectsRes = await fetch("/api/prospects");
      const prospectsData = await prospectsRes.json();
      const prospects = prospectsData.prospects || [];
      
      const contacted = prospects.filter((p: any) => p.stage === 'Contacted').length;
      const replied = prospects.filter((p: any) => ['Replied', 'Negotiating'].includes(p.stage)).length;
      
      setStats({
        total: prospects.length,
        contacted,
        replied,
        activePartners: 1 // Audrey Mora
      });
    } catch (error) {
      console.error("Failed to fetch data:", error);
    } finally {
      setLoading(false);
    }
  }

  function getStatusColor(status: string) {
    switch (status) {
      case "active":
        return "text-green-400 border-green-400";
      case "idle":
        return "text-yellow-400 border-yellow-400";
      case "error":
        return "text-red-400 border-red-400";
      default:
        return "text-gray-400 border-gray-400";
    }
  }

  function getStatusDot(status: string) {
    switch (status) {
      case "active":
        return "🟢";
      case "idle":
        return "🟡";
      case "error":
        return "🔴";
      default:
        return "⚪";
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
        <div className="text-gray-400">Loading...</div>
      </div>
    );
  }

  const borderColor = agentStatus 
    ? getStatusColor(agentStatus.status).split(" ")[1] 
    : "border-gray-600";

  return (
    <div className="space-y-6">
      <div className="text-xs text-gray-600">v2.0.0-nextjs</div>

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
                {agentStatus ? timeSince(agentStatus.lastHeartbeat) : "—"}
              </span>
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Current Task</p>
            <p className="text-lg font-medium">
              {agentStatus?.currentTask || "Unknown"}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard 
          title="Total Pipeline" 
          value={stats.total.toString()} 
          subtitle="of 95 target" 
          color="green" 
        />
        <StatCard 
          title="Contacted" 
          value={stats.contacted.toString()} 
          subtitle="outreach sent" 
          color="blue" 
        />
        <StatCard 
          title="Reply Rate" 
          value={stats.replied > 0 ? `${Math.round((stats.replied / stats.contacted) * 100)}%` : "0%"} 
          subtitle={`${stats.replied} replies`} 
          color="yellow" 
        />
        <StatCard 
          title="Active Partners" 
          value={stats.activePartners.toString()} 
          subtitle="Audrey Mora" 
          color="purple" 
        />
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4">📜 Recent Activity</h3>
        {activity.length > 0 ? (
          <div className="space-y-3">
            {activity.map((item, i) => (
              <div key={i} className="flex items-center gap-3 text-sm">
                <span className="text-gray-500">
                  {new Date(item.createdAt).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
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
