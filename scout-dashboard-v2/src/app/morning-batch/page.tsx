"use client";

import { useEffect, useState } from "react";

interface Prospect {
  name: string;
  handle: string;
  city: string;
  email: string;
  stage: string;
  branch: string;
  score: number;
  draft_status?: string;
}

export default function MorningBatch() {
  const [prospects, setProspects] = useState<Prospect[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProspects();
  }, []);

  async function fetchProspects() {
    try {
      const res = await fetch("/api/prospects?stage=Prospected");
      const data = await res.json();
      setProspects(data.prospects || []);
    } catch (error) {
      console.error("Failed to fetch prospects:", error);
    } finally {
      setLoading(false);
    }
  }

  async function approveProspect(name: string) {
    // This would update the prospect status
    alert(`Approved ${name} - implement API call to update draft_status`);
  }

  const highPriority = prospects.filter(p => p.score >= 4);
  const regular = prospects.filter(p => p.score < 4);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading morning batch...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Morning Batch</h1>
        <p className="text-gray-400">{prospects.length} prospects ready for outreach approval</p>
      </div>

      {highPriority.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-yellow-400">🔥 High Priority (Score 4-5)</h2>
          <div className="grid gap-4">
            {highPriority.map((prospect, i) => (
              <ProspectCard key={i} prospect={prospect} onApprove={() => approveProspect(prospect.name)} />
            ))}
          </div>
        </div>
      )}

      {regular.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-400">Regular Priority</h2>
          <div className="grid gap-4">
            {regular.map((prospect, i) => (
              <ProspectCard key={i} prospect={prospect} onApprove={() => approveProspect(prospect.name)} />
            ))}
          </div>
        </div>
      )}

      {prospects.length === 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 text-center">
          <p className="text-gray-400">No prospects in "Prospected" stage.</p>
          <p className="text-sm text-gray-500 mt-2">Run prospecting to find more leads.</p>
        </div>
      )}
    </div>
  );
}

function ProspectCard({ prospect, onApprove }: { prospect: Prospect; onApprove: () => void }) {
  const [showDraft, setShowDraft] = useState(false);

  const draft = generateDraft(prospect);

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-semibold text-lg">{prospect.name}</h3>
          <p className="text-gray-400 text-sm">@{prospect.handle} • {prospect.city} • {prospect.branch}</p>
          <div className="flex gap-1 mt-2">
            {Array.from({ length: prospect.score }).map((_, j) => (
              <span key={j} className="text-yellow-500">★</span>
            ))}
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowDraft(!showDraft)}
            className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm"
          >
            {showDraft ? "Hide Draft" : "View Draft"}
          </button>
          <button
            onClick={onApprove}
            className="px-4 py-2 bg-green-600 hover:bg-green-500 rounded-lg text-sm font-medium"
          >
            Approve
          </button>
        </div>
      </div>

      {showDraft && (
        <div className="mt-4 p-4 bg-gray-950 rounded-lg border border-gray-800">
          <pre className="text-sm text-gray-300 whitespace-pre-wrap">{draft}</pre>
        </div>
      )}
    </div>
  );
}

function generateDraft(prospect: Prospect): string {
  return `Hi ${prospect.name.split(' ')[0]},

This is Keri! I'm a pianist, music teacher, and co-founder of Thoven — an all-in-one music education platform where families can find verified, background-checked teachers trained at top schools like The Juilliard School.

We'd be happy to structure this in a way that works best for you:
- Affiliate partnership: Earn commission on every lesson booked
- Complimentary lessons: Free lessons for your family to experience the platform

Looking forward to connecting!

Keri Erten
Co-Founder & CXO`;
}
