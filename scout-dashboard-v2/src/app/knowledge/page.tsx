"use client";

import { useState } from "react";

interface Interaction {
  id: string;
  prospectName: string;
  prospectBranch: string;
  situation: string;
  guidance?: string;
  response?: string;
  outcome?: string;
  patternTag?: string;
  createdAt: string;
}

const SAMPLE_INTERACTIONS: Interaction[] = [
  {
    id: "1",
    prospectName: "Audrey Mora",
    prospectBranch: "Mom Influencers (IG)",
    situation: "Initial outreach — interested but asked about pricing",
    guidance: "Offer $200 lesson credit model, don't mention revenue share yet",
    response: "Hi Audrey! We'd love to offer you $200 in lesson credits to experience Thoven with your family...",
    outcome: "Accepted — live partner since Feb 23",
    patternTag: "pricing question from mom influencer",
    createdAt: "2026-02-20T10:00:00Z"
  },
  {
    id: "2",
    prospectName: "Sample Homeschool Mom",
    prospectBranch: "Homeschool Influencers (AZ)",
    situation: "Replied asking if ESA-eligible",
    guidance: "Lead with ClassWallet integration, mention ESA eligibility upfront",
    response: "Yes! Thoven is ESA-eligible in Arizona through ClassWallet...",
    outcome: "Pending reply",
    patternTag: "ESA question from homeschool prospect",
    createdAt: "2026-03-25T14:30:00Z"
  }
];

const PATTERN_TAGS = [
  "All",
  "pricing question from mom influencer",
  "ESA question from homeschool prospect",
  "interested no questions",
  "declined timing",
  "declined not fit",
  "asking about rates",
  "asking about partnership terms"
];

function InteractionCard({ interaction }: { interaction: Interaction }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h3 className="font-semibold">{interaction.prospectName}</h3>
            <span className="text-xs px-2 py-1 bg-gray-800 rounded-full text-gray-400">{interaction.prospectBranch}</span>
            {interaction.patternTag && (
              <span className="text-xs px-2 py-1 bg-blue-900 rounded-full text-blue-300">{interaction.patternTag}</span>
            )}
          </div>
          <p className="text-gray-400 text-sm mt-1">{new Date(interaction.createdAt).toLocaleDateString()}</p>
          <p className="text-gray-300 mt-2"><span className="text-gray-500">Situation:</span> {interaction.situation}</p>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition"
        >
          {expanded ? "Collapse" : "Expand"}
        </button>
      </div>

      {expanded && (
        <div className="mt-4 space-y-3 border-t border-gray-800 pt-4">
          {interaction.guidance && (
            <div className="bg-gray-950 rounded-lg p-4">
              <p className="text-xs text-gray-500 mb-1">🎯 Guidance from Andres:</p>
              <p className="text-sm text-yellow-300">{interaction.guidance}</p>
            </div>
          )}
          
          {interaction.response && (
            <div className="bg-gray-950 rounded-lg p-4">
              <p className="text-xs text-gray-500 mb-1">📧 Scout Response:</p>
              <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono">{interaction.response}</pre>
            </div>
          )}
          
          {interaction.outcome && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">Outcome:</span>
              <span className={`text-sm ${interaction.outcome.includes('Accepted') || interaction.outcome.includes('Partner') ? 'text-green-400' : 'text-gray-400'}`}>
                {interaction.outcome}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function KnowledgeBase() {
  const [interactions, setInteractions] = useState<Interaction[]>(SAMPLE_INTERACTIONS);
  const [tagFilter, setTagFilter] = useState("All");
  const [search, setSearch] = useState("");
  const [newInteractionOpen, setNewInteractionOpen] = useState(false);
  const [newInteraction, setNewInteraction] = useState<Partial<Interaction>>({
    createdAt: new Date().toISOString()
  });

  const filteredInteractions = interactions.filter(i => {
    const matchesTag = tagFilter === "All" || i.patternTag === tagFilter;
    const matchesSearch = search === "" || 
      i.prospectName.toLowerCase().includes(search.toLowerCase()) ||
      i.situation.toLowerCase().includes(search.toLowerCase()) ||
      i.patternTag?.toLowerCase().includes(search.toLowerCase());
    return matchesTag && matchesSearch;
  });

  const patternStats = interactions.reduce((acc, i) => {
    if (i.patternTag) {
      acc[i.patternTag] = (acc[i.patternTag] || 0) + 1;
    }
    return acc;
  }, {} as Record<string, number>);

  function handleAddInteraction() {
    if (newInteraction.prospectName && newInteraction.situation) {
      setInteractions([{
        ...newInteraction as Interaction,
        id: Date.now().toString(),
        createdAt: new Date().toISOString()
      }, ...interactions]);
      setNewInteractionOpen(false);
      setNewInteraction({ createdAt: new Date().toISOString() });
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Knowledge Base</h1>
          <p className="text-gray-400">Logged interactions and patterns for learning</p>
        </div>
        <button
          onClick={() => setNewInteractionOpen(!newInteractionOpen)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium transition"
        >
          {newInteractionOpen ? 'Cancel' : '+ Log Interaction'}
        </button>
      </div>

      {/* Pattern Stats */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <h3 className="text-sm font-semibold text-gray-500 mb-3">Pattern Tags</h3>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setTagFilter("All")}
            className={`px-3 py-1 rounded-full text-xs transition ${
              tagFilter === "All" ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400'
            }`}
          >
            All ({interactions.length})
          </button>
          {Object.entries(patternStats).map(([tag, count]) => (
            <button
              key={tag}
              onClick={() => setTagFilter(tagFilter === tag ? "All" : tag)}
              className={`px-3 py-1 rounded-full text-xs transition ${
                tagFilter === tag ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400'
              }`}
            >
              {tag} ({count})
            </button>
          ))}
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <input
          type="text"
          placeholder="Search interactions..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-gray-900 border border-gray-800 rounded-lg px-4 py-2 text-sm flex-1"
        />
      </div>

      {/* Add New Interaction */}
      {newInteractionOpen && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h3 className="font-semibold mb-4">Log New Interaction</h3>
          <div className="grid grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Prospect name"
              value={newInteraction.prospectName || ''}
              onChange={(e) => setNewInteraction({...newInteraction, prospectName: e.target.value})}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2"
            />
            <select
              value={newInteraction.prospectBranch || 'Mom Influencers (IG)'}
              onChange={(e) => setNewInteraction({...newInteraction, prospectBranch: e.target.value})}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2"
            >
              <option>Mom Influencers (IG)</option>
              <option>Mom Influencers (TikTok/YouTube)</option>
              <option>Mom Blogs</option>
              <option>Homeschool Influencers (AZ)</option>
              <option>Homeschool Blogs (AZ)</option>
              <option>Homeschool Expansion</option>
            </select>
          </div>          
          <div className="mt-4 space-y-3">
            <textarea
              placeholder="Situation (what happened?)"
              value={newInteraction.situation || ''}
              onChange={(e) => setNewInteraction({...newInteraction, situation: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 h-20"
            />
            <textarea
              placeholder="Guidance from Andres (what should Scout do?)"
              value={newInteraction.guidance || ''}
              onChange={(e) => setNewInteraction({...newInteraction, guidance: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 h-20"
            />
            <textarea
              placeholder="Scout Response (what was sent)"
              value={newInteraction.response || ''}
              onChange={(e) => setNewInteraction({...newInteraction, response: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 h-20"
            />
            <div className="grid grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Outcome (e.g., Converted, Cold, Pending)"
                value={newInteraction.outcome || ''}
                onChange={(e) => setNewInteraction({...newInteraction, outcome: e.target.value})}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2"
              />
              <select
                value={newInteraction.patternTag || ''}
                onChange={(e) => setNewInteraction({...newInteraction, patternTag: e.target.value})}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2"
              >
                <option value="">Select pattern tag...</option>
                {PATTERN_TAGS.slice(1).map(tag => <option key={tag} value={tag}>{tag}</option>)}
              </select>
            </div>
          </div>
          <div className="mt-4 flex justify-end">
            <button
              onClick={handleAddInteraction}
              className="px-4 py-2 bg-green-600 hover:bg-green-500 rounded-lg text-sm font-medium"
            >
              Log Interaction
            </button>
          </div>
        </div>
      )}

      {/* Interactions List */}
      <div className="space-y-4">
        {filteredInteractions.map((interaction) => (
          <InteractionCard key={interaction.id} interaction={interaction} />
        ))}
      </div>

      {filteredInteractions.length === 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center">
          <p className="text-gray-400">No interactions found.</p>
          <p className="text-sm text-gray-500 mt-2">Log your first interaction to start building the knowledge base.</p>
        </div>
      )}
    </div>
  );
}
