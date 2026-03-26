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
  scoreReason?: string;
}

const STAGE_COLORS: Record<string, string> = {
  Uncontacted: "bg-gray-800 text-gray-400",
  Prospected: "bg-yellow-900 text-yellow-300",
  Contacted: "bg-blue-900 text-blue-300",
  Replied: "bg-green-900 text-green-300",
  Negotiating: "bg-purple-900 text-purple-300",
  Declined: "bg-red-900 text-red-300",
  Partner: "bg-green-700 text-green-100",
};

const BRANCHES = [
  "All",
  "Mom Influencers (IG)",
  "Mom Influencers (TikTok/YouTube)",
  "Mom Blogs",
  "Homeschool Influencers (AZ)",
  "Homeschool Blogs (AZ)",
  "Homeschool Expansion",
];

const CITIES = ["All", "Miami", "LA", "SF", "Houston", "Chicago", "NYC", "Dallas", "Austin", "Arizona"];

const STAGES = ["All", "Uncontacted", "Prospected", "Contacted", "Replied", "Negotiating", "Declined", "Partner"];

function ScoreStars({ score, reason }: { score: number; reason?: string }) {
  const [showTooltip, setShowTooltip] = useState(false);
  
  return (
    <div 
      className="relative inline-flex items-center gap-1 cursor-help"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      {Array.from({ length: 5 }).map((_, i) => (
        <span key={i} className={i < score ? "text-yellow-500" : "text-gray-700"}>★</span>
      ))}
      {showTooltip && reason && (
        <div className="absolute bottom-full left-0 mb-2 w-64 p-3 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50">
          <p className="text-xs text-gray-300">{reason}</p>
        </div>
      )}
    </div>
  );
}

export default function Pipeline() {
  const [prospects, setProspects] = useState<Prospect[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [branchFilter, setBranchFilter] = useState("All");
  const [cityFilter, setCityFilter] = useState("All");
  const [stageFilter, setStageFilter] = useState("All");

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

  const filteredProspects = prospects.filter(p => {
    const matchesSearch = search === "" || 
      p.name?.toLowerCase().includes(search.toLowerCase()) ||
      p.handle?.toLowerCase().includes(search.toLowerCase()) ||
      p.email?.toLowerCase().includes(search.toLowerCase());
    const matchesBranch = branchFilter === "All" || p.branch === branchFilter;
    const matchesCity = cityFilter === "All" || p.city === cityFilter;
    const matchesStage = stageFilter === "All" || p.stage === stageFilter;
    return matchesSearch && matchesBranch && matchesCity && matchesStage;
  });

  const stageCounts = prospects.reduce((acc, p) => {
    acc[p.stage] = (acc[p.stage] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const formatFollowers = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

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
          <p className="text-gray-400">{filteredProspects.length} of {prospects.length} prospects</p>
        </div>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Search name, handle, email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm w-64"
          />
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-4 bg-gray-900 border border-gray-800 rounded-xl p-4">
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">Branch:</span>
          <select 
            value={branchFilter} 
            onChange={(e) => setBranchFilter(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded px-3 py-1 text-sm"
          >
            {BRANCHES.map(b => <option key={b} value={b}>{b}</option>)}
          </select>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">City:</span>
          <select 
            value={cityFilter} 
            onChange={(e) => setCityFilter(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded px-3 py-1 text-sm"
          >
            {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">Stage:</span>
          <select 
            value={stageFilter} 
            onChange={(e) => setStageFilter(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded px-3 py-1 text-sm"
          >
            {STAGES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      </div>

      {/* Stage Summary */}
      <div className="grid grid-cols-7 gap-2">
        {STAGES.slice(1).map(stage => (
          <div key={stage} className="bg-gray-900 border border-gray-800 rounded-xl p-3 text-center">
            <p className="text-xl font-bold text-blue-400">{stageCounts[stage] || 0}</p>
            <p className="text-xs text-gray-500 truncate">{stage}</p>
          </div>
        ))}
      </div>

      {/* Pipeline Table */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-800 text-gray-400">
            <tr>
              <th className="text-left p-4">Name/Handle</th>
              <th className="text-left p-4">Location</th>
              <th className="text-left p-4">Branch</th>
              <th className="text-left p-4">Followers</th>
              <th className="text-left p-4">Stage</th>
              <th className="text-left p-4">Score</th>
              <th className="text-left p-4">Email</th>
            </tr>
          </thead>
          <tbody>
            {filteredProspects.map((prospect, i) => (
              <tr key={i} className="border-t border-gray-800 hover:bg-gray-800/50 transition">
                <td className="p-4">
                  <div className="font-medium">{prospect.name}</div>
                  <div className="text-gray-500 text-xs">@{prospect.handle}</div>
                </td>
                <td className="p-4 text-gray-400">{prospect.city}</td>
                <td className="p-4 text-gray-400">{prospect.branch}</td>
                <td className="p-4 text-gray-400">{formatFollowers(prospect.followers)}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded-full text-xs ${STAGE_COLORS[prospect.stage] || STAGE_COLORS.Uncontacted}`}>
                    {prospect.stage}
                  </span>
                </td>
                <td className="p-4">
                  <ScoreStars score={prospect.score} reason={prospect.scoreReason || `Score based on ${prospect.email ? 'email found' : 'no email'} + ${prospect.followers > 100000 ? 'high follower count' : 'moderate reach'}`} />
                </td>
                <td className="p-4">
                  {prospect.email ? (
                    <span className="text-green-400 text-xs">{prospect.email}</span>
                  ) : (
                    <span className="text-red-400 text-xs">No email</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filteredProspects.length === 0 && (
          <div className="p-8 text-center text-gray-500">No prospects match your filters</div>
        )}
      </div>
    </div>
  );
}
