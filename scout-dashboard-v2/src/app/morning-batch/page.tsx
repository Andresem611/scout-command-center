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
  draftStatus?: string;
  nextFollowUp?: string;
}

interface DraftItem {
  prospect: Prospect;
  subject: string;
  body: string;
  type: 'initial' | 'followup-day3' | 'followup-day7' | 'followup-day14';
}

const EMAIL_TEMPLATE = `Hi [name],

This is Keri! I'm a pianist, music teacher, and co-founder of Thoven — an all-in-one music education platform where families can find verified, background-checked teachers trained at top schools like The Juilliard School and book lessons easily, anytime, anywhere.

[ESA_NOTE]

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

Looking forward to connecting!

Keri Erten
Co-Founder & CXO
Music Educator & Pianist`;

const FOLLOWUP_TEMPLATES = {
  'day3': `Hi [name],

Just bumping this — would love to connect if you're interested!

Keri`,
  'day7': `Hi [name],

Quick follow-up! One thing parents love about Thoven: they can track their child's progress in real-time through our dashboard. Happy to show you how it works.

Interested in a quick chat?

Keri`,
  'day14': `Hi [name],

Totally understand if the timing isn't right — happy to connect anytime if things change.

Keri`
};

function generateDraft(prospect: Prospect, type: DraftItem['type']): DraftItem {
  let subject = "Partnership opportunity — music education for your audience";
  let body = EMAIL_TEMPLATE;
  
  // Add ESA note for homeschool prospects
  const esaNote = prospect.branch.includes('Homeschool') 
    ? "Thoven is ESA-eligible in Arizona through ClassWallet, making it easy for homeschool families to use their education savings.\n\n"
    : "";
  
  body = body.replace('[ESA_NOTE]', esaNote);
  body = body.replace(/\[name\]/g, prospect.name.split(' ')[0]);
  
  if (type === 'followup-day3') {
    subject = "Re: Partnership opportunity";
    body = FOLLOWUP_TEMPLATES['day3'].replace(/\[name\]/g, prospect.name.split(' ')[0]);
  } else if (type === 'followup-day7') {
    subject = "Re: Partnership opportunity — progress tracking feature";
    body = FOLLOWUP_TEMPLATES['day7'].replace(/\[name\]/g, prospect.name.split(' ')[0]);
  } else if (type === 'followup-day14') {
    subject = "Re: Partnership opportunity";
    body = FOLLOWUP_TEMPLATES['day14'].replace(/\[name\]/g, prospect.name.split(' ')[0]);
  }
  
  return { prospect, subject, body, type };
}

function DraftCard({ 
  draft, 
  onApprove, 
  onRemove 
}: { 
  draft: DraftItem; 
  onApprove: () => void;
  onRemove: () => void;
}) {
  const [showDraft, setShowDraft] = useState(false);
  
  const typeLabels: Record<DraftItem['type'], string> = {
    'initial': '📧 Initial Outreach',
    'followup-day3': '📧 Follow-up (Day 3)',
    'followup-day7': '📧 Follow-up (Day 7)',
    'followup-day14': '📧 Follow-up (Day 14)'
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h3 className="font-semibold text-lg">{draft.prospect.name}</h3>
            <span className="text-xs px-2 py-1 bg-gray-800 rounded-full text-gray-400">{typeLabels[draft.type]}</span>
          </div>
          <p className="text-gray-400 text-sm">@{draft.prospect.handle} • {draft.prospect.city} • {draft.prospect.branch}</p>
          <div className="flex items-center gap-2 mt-2">
            {Array.from({ length: draft.prospect.score }).map((_, j) => (
              <span key={j} className="text-yellow-500 text-sm">★</span>
            ))}
            <span className="text-gray-500 text-xs ml-2">{draft.prospect.email}</span>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowDraft(!showDraft)}
            className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition"
          >
            {showDraft ? "Hide Draft" : "View Draft"}
          </button>
          <button
            onClick={onApprove}
            className="px-4 py-2 bg-green-600 hover:bg-green-500 rounded-lg text-sm font-medium transition"
          >
            Approve
          </button>
          <button
            onClick={onRemove}
            className="px-4 py-2 bg-red-900/50 hover:bg-red-900 text-red-400 rounded-lg text-sm transition"
          >
            Skip
          </button>
        </div>
      </div>

      {showDraft && (
        <div className="mt-4 p-4 bg-gray-950 rounded-lg border border-gray-800">
          <p className="text-xs text-gray-500 mb-2">Subject: {draft.subject}</p>
          <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono">{draft.body}</pre>
        </div>
      )}
    </div>
  );
}

function ReadyToSendCard({ 
  draft, 
  onSend, 
  onRevert 
}: { 
  draft: DraftItem; 
  onSend: () => void;
  onRevert: () => void;
}) {
  const [showDraft, setShowDraft] = useState(false);
  
  const typeLabels: Record<DraftItem['type'], string> = {
    'initial': '📧 Initial Outreach',
    'followup-day3': '📧 Follow-up (Day 3)',
    'followup-day7': '📧 Follow-up (Day 7)',
    'followup-day14': '📧 Follow-up (Day 14)'
  };

  return (
    <div className="bg-green-950/30 border border-green-800 rounded-xl p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h3 className="font-semibold text-lg text-green-100">{draft.prospect.name}</h3>
            <span className="text-xs px-2 py-1 bg-green-900 rounded-full text-green-300">{typeLabels[draft.type]}</span>
            <span className="text-xs px-2 py-1 bg-green-800 rounded-full text-green-200">✓ Approved</span>
          </div>
          <p className="text-green-200/60 text-sm">@{draft.prospect.handle} • {draft.prospect.city}</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowDraft(!showDraft)}
            className="px-4 py-2 bg-green-900/50 hover:bg-green-900 text-green-300 rounded-lg text-sm transition"
          >
            {showDraft ? "Hide" : "View"}
          </button>
          <button
            onClick={onRevert}
            className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-400 rounded-lg text-sm transition"
          >
            Revert
          </button>
          <button
            onClick={onSend}
            className="px-4 py-2 bg-green-600 hover:bg-green-500 rounded-lg text-sm font-medium transition"
          >
            Send Now
          </button>
        </div>
      </div>

      {showDraft && (
        <div className="mt-4 p-4 bg-gray-950 rounded-lg border border-green-800">
          <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono">{draft.body}</pre>
        </div>
      )}
    </div>
  );
}

export default function MorningBatch() {
  const [prospects, setProspects] = useState<Prospect[]>([]);
  const [readyToSend, setReadyToSend] = useState<DraftItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [sentToday, setSentToday] = useState(0);

  useEffect(() => {
    fetchProspects();
  }, []);

  async function fetchProspects() {
    try {
      const res = await fetch("/api/prospects");
      const data = await res.json();
      const allProspects = data.prospects || [];
      setProspects(allProspects);
    } catch (error) {
      console.error("Failed to fetch prospects:", error);
    } finally {
      setLoading(false);
    }
  }

  // Generate drafts from prospected prospects
  const pendingDrafts: DraftItem[] = prospects
    .filter(p => p.stage === 'Prospected' && p.email && !readyToSend.some(r => r.prospect.name === p.name))
    .map(p => generateDraft(p, 'initial'));

  // Generate follow-ups for contacted prospects
  const followupDrafts: DraftItem[] = prospects
    .filter(p => {
      if (p.stage !== 'Contacted') return false;
      // Check if follow-up is due (mock logic - would check actual dates)
      return p.nextFollowUp && new Date(p.nextFollowUp) <= new Date();
    })
    .map(p => {
      const daysSince = 3; // Would calculate from actual contact date
      const type: DraftItem['type'] = daysSince <= 3 ? 'followup-day3' : daysSince <= 7 ? 'followup-day7' : 'followup-day14';
      return generateDraft(p, type);
    });

  const highPriority = pendingDrafts.filter(d => d.prospect.score >= 4);
  const regular = pendingDrafts.filter(d => d.prospect.score < 4);

  function approveDraft(draft: DraftItem) {
    setReadyToSend([...readyToSend, draft]);
  }

  function removeDraft(draft: DraftItem) {
    // In real implementation, would update prospect status to 'Skipped' or similar
    alert(`Skipped ${draft.prospect.name} — implement status update`);
  }

  function revertDraft(draft: DraftItem) {
    setReadyToSend(readyToSend.filter(d => d.prospect.name !== draft.prospect.name));
  }

  async function sendDraft(draft: DraftItem) {
    // In real implementation, would call AgentMail API
    alert(`Sending to ${draft.prospect.name}...\n\nIn production, this would:\n1. Call AgentMail API\n2. Update prospect stage to 'Contacted'\n3. Log activity\n4. Schedule follow-up`);
    setReadyToSend(readyToSend.filter(d => d.prospect.name !== draft.prospect.name));
    setSentToday(sentToday + 1);
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading morning batch...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Morning Batch</h1>
          <p className="text-gray-400">Review and approve outreach for today</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500">Sent Today</p>
          <p className="text-2xl font-bold text-green-400">{sentToday}</p>
        </div>
      </div>

      {/* Ready to Send Queue */}
      {readyToSend.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-green-400">✓ Ready to Send ({readyToSend.length})</h2>
            <button 
              onClick={() => alert('Send all functionality would trigger here')}
              className="px-4 py-2 bg-green-600 hover:bg-green-500 rounded-lg text-sm font-medium transition"
            >
              Send All Approved
            </button>
          </div>
          <div className="space-y-3">
            {readyToSend.map((draft, i) => (
              <ReadyToSendCard 
                key={i} 
                draft={draft} 
                onSend={() => sendDraft(draft)}
                onRevert={() => revertDraft(draft)}
              />
            ))}
          </div>
        </div>
      )}

      {/* High Priority */}
      {highPriority.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-yellow-400">🔥 High Priority (Score 4-5)</h2>
          <div className="space-y-3">
            {highPriority.map((draft, i) => (
              <DraftCard 
                key={i} 
                draft={draft} 
                onApprove={() => approveDraft(draft)}
                onRemove={() => removeDraft(draft)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Regular Priority */}
      {regular.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-400">Regular Priority</h2>
          <div className="space-y-3">
            {regular.map((draft, i) => (
              <DraftCard 
                key={i} 
                draft={draft} 
                onApprove={() => approveDraft(draft)}
                onRemove={() => removeDraft(draft)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Follow-ups */}
      {followupDrafts.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-blue-400">🔄 Follow-ups Due</h2>
          <div className="space-y-3">
            {followupDrafts.map((draft, i) => (
              <DraftCard 
                key={i} 
                draft={draft} 
                onApprove={() => approveDraft(draft)}
                onRemove={() => removeDraft(draft)}
              />
            ))}
          </div>
        </div>
      )}

      {pendingDrafts.length === 0 && readyToSend.length === 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center">
          <p className="text-gray-400 text-lg">No prospects waiting for approval.</p>
          <p className="text-sm text-gray-500 mt-2">Run prospecting to find more leads, or check back later for follow-ups.</p>
        </div>
      )}
    </div>
  );
}
