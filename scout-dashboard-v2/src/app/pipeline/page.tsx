"use client";

import { useEffect, useState } from "react";

interface Prospect {
  name: string;
  handle: string;
  followers: number;
  city: string;
  email: string;
  stage: string;
  type: string;
  branch: string;
  score: number;
}

export default function Pipeline() {
  const [prospects, setProspects] = useState<Prospect[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    fetchProspects();
  }, []);

  async function fetchProspects() {
    try {
      const res = await fetch("/api/prospects");
      const data = await res.json();
      setProspects(data.prospects || []);
    } catch (error) {
      console.error("Failed to fetch prospects:", error);
    } finally {
      setLoading(false);
    }
  }

  const filteredProspects = prospects.filter(p => 
    p.name?.toLowerCase().includes(filter.toLowerCase()) ||
    p.city?.toLowerCase().includes(filter.toLowerCase()) ||
    p.branch?.toLowerCase().includes(filter.toLowerCase())
  );

  const stageCounts = prospects.reduce((acc, p) => {
    acc[p.stage] = (acc[p.stage] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading pipeline...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Pipeline</h1>
          <p className="text-gray-400">{prospects.length} prospects across all branches</p>
        </div>
        <input
          type="text"
          placeholder="Filter prospects..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm w-64"
        />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Object.entries(stageCounts).map(([stage, count]) => (
          <div key={stage} className="bg-gray-900 border border-gray-800 rounded-xl p-4 text-center">
            <p className="text-2xl font-bold text-blue-400">{count}</p>
            <p className="text-sm text-gray-500">{stage}</p>
          </div>
        ))}
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-800 text-gray-400">
            <tr>
              <th className="text-left p-4">Name</th>
              <th className="text-left p-4">City</th>
              <th className="text-left p-4">Branch</th>
              <th className="text-left p-4">Stage</th>
              <th className="text-left p-4">Score</th>
            </tr>
          </thead>
          <tbody>
            {filteredProspects.map((prospect, i) => (
              <tr key={i} className="border-t border-gray-800 hover:bg-gray-800/50">
                <td className="p-4">
                  <div className="font-medium">{prospect.name}</div>
                  <div className="text-gray-500 text-xs">@{prospect.handle}</div>
                </td>
                <td className="p-4 text-gray-400">{prospect.city}</td>
                <td className="p-4 text-gray-400">{prospect.branch}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    prospect.stage === 'Contacted' ? 'bg-blue-900 text-blue-300' :
                    prospect.stage === 'Replied' ? 'bg-green-900 text-green-300' :
                    prospect.stage === 'Prospected' ? 'bg-yellow-900 text-yellow-300' :
                    'bg-gray-800 text-gray-400'
                  }`}>
                    {prospect.stage}
                  </span>
                </td>
                <td className="p-4">
                  <div className="flex gap-1">
                    {Array.from({ length: prospect.score }).map((_, j) => (
                      <span key={j} className="text-yellow-500">★</span>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
