"use client";

import { useEffect, useState } from "react";

interface Reply {
  id: string;
  prospectName: string;
  prospectEmail: string;
  subject: string;
  preview: string;
  type: 'INTERESTED' | 'QUESTIONS' | 'DECLINED' | 'RATES' | 'OUT_OF_OFFICE' | 'SPAM';
  status: 'unread' | 'read' | 'handled';
  receivedAt: string;
}

const REPLY_TYPE_COLORS: Record<Reply['type'], string> = {
  'INTERESTED': 'bg-green-900 text-green-300',
  'QUESTIONS': 'bg-blue-900 text-blue-300',
  'DECLINED': 'bg-red-900 text-red-300',
  'RATES': 'bg-yellow-900 text-yellow-300',
  'OUT_OF_OFFICE': 'bg-gray-800 text-gray-400',
  'SPAM': 'bg-gray-800 text-gray-500'
};

const REPLY_TYPE_LABELS: Record<Reply['type'], string> = {
  'INTERESTED': '🔥 Interested',
  'QUESTIONS': '❓ Questions',
  'DECLINED': '❌ Declined',
  'RATES': '💰 Rates/Terms',
  'OUT_OF_OFFICE': '📤 Out of Office',
  'SPAM': '🗑️ Spam'
};

const SAMPLE_REPLIES: Reply[] = [
  {
    id: "1",
    prospectName: "Christie Ferrari",
    prospectEmail: "christieferrari@outlook.com",
    subject: "Re: Partnership opportunity",
    preview: "Thanks for reaching out! I'd love to learn more about Thoven...",
    type: "INTERESTED",
    status: "unread",
    receivedAt: "2026-03-27T10:00:00Z"
  },
  {
    id: "2",
    prospectName: "Gaby Castellar",
    prospectEmail: "info@gabycastellar.com",
    subject: "Re: Partnership opportunity",
    preview: "What commission rate are you offering for affiliates?",
    type: "RATES",
    status: "read",
    receivedAt: "2026-03-26T14:30:00Z"
  }
];

export default function Inbox() {
  const [replies, setReplies] = useState<Reply[]>(SAMPLE_REPLIES);
  const [filter, setFilter] = useState<Reply['type'] | 'All'>('All');

  const filteredReplies = filter === 'All' 
    ? replies 
    : replies.filter(r => r.type === filter);

  const typeCounts = replies.reduce((acc, r) => {
    acc[r.type] = (acc[r.type] || 0) + 1;
    return acc;
  }, {} as Record<Reply['type'], number>);

  const unreadCount = replies.filter(r => r.status === 'unread').length;

  function markAsHandled(id: string) {
    setReplies(replies.map(r => r.id === id ? {...r, status: 'handled'} : r));
  }

  function markAsRead(id: string) {
    setReplies(replies.map(r => r.id === id ? {...r, status: 'read'} : r));
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Inbox Summary</h1>
          <p className="text-gray-400">Reply classification and tracking</p>
        </div>
        {unreadCount > 0 && (
          <div className="bg-red-900/50 border border-red-800 rounded-lg px-4 py-2">
            <span className="text-red-300 font-medium">🔔 {unreadCount} unread replies need attention</span>
          </div>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-6 gap-3">
        <button
          onClick={() => setFilter('All')}
          className={`bg-gray-900 border rounded-xl p-4 text-center transition ${
            filter === 'All' ? 'border-blue-500' : 'border-gray-800'
          }`}
        >
          <p className="text-2xl font-bold text-blue-400">{replies.length}</p>
          <p className="text-xs text-gray-500">Total</p>
        </button>
        
        {(Object.keys(REPLY_TYPE_LABELS) as Reply['type'][]).map(type => (
          <button
            key={type}
            onClick={() => setFilter(filter === type ? 'All' : type)}
            className={`bg-gray-900 border rounded-xl p-4 text-center transition ${
              filter === type ? 'border-blue-500' : 'border-gray-800'
            }`}
          >
            <p className="text-2xl font-bold text-blue-400">{typeCounts[type] || 0}</p>
            <p className="text-xs text-gray-500 truncate">{REPLY_TYPE_LABELS[type].split(' ')[1]}</p>
          </button>
        ))}
      </div>

      {/* Note */}
      <div className="bg-blue-950/30 border border-blue-900 rounded-xl p-4">
        <p className="text-sm text-blue-300">
          💡 <strong>Alert System:</strong> When real replies come in, Scout will email keri@thoven.co immediately 
          and alert you in chat. This page shows a summary only — detailed responses are handled in your primary inbox.
        </p>
      </div>

      {/* Replies List */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-800 text-gray-400">
            <tr>
              <th className="text-left p-4">From</th>
              <th className="text-left p-4">Preview</th>
              <th className="text-left p-4">Type</th>
              <th className="text-left p-4">Received</th>
              <th className="text-left p-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredReplies.map((reply) => (
              <tr 
                key={reply.id} 
                className={`border-t border-gray-800 hover:bg-gray-800/50 transition ${
                  reply.status === 'unread' ? 'bg-blue-950/10' : ''
                }`}
              >
                <td className="p-4">
                  <div className="font-medium">{reply.prospectName}</div>
                  <div className="text-gray-500 text-xs">{reply.prospectEmail}</div>
                </td>
                <td className="p-4">
                  <div className="font-medium text-gray-300">{reply.subject}</div>
                  <div className="text-gray-500 text-xs truncate max-w-md">{reply.preview}</div>
                </td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded-full text-xs ${REPLY_TYPE_COLORS[reply.type]}`}>
                    {REPLY_TYPE_LABELS[reply.type]}
                  </span>
                </td>
                <td className="p-4 text-gray-400">
                  {new Date(reply.receivedAt).toLocaleDateString()}
                </td>
                <td className="p-4">
                  <div className="flex gap-2">
                    {reply.status === 'unread' && (
                      <button
                        onClick={() => markAsRead(reply.id)}
                        className="text-xs px-3 py-1 bg-blue-900 text-blue-300 rounded hover:bg-blue-800 transition"
                      >
                        Mark Read
                      </button>
                    )}
                    {reply.status !== 'handled' && (
                      <button
                        onClick={() => markAsHandled(reply.id)}
                        className="text-xs px-3 py-1 bg-green-900 text-green-300 rounded hover:bg-green-800 transition"
                      >
                        Handled
                      </button>
                    )}
                    {reply.status === 'handled' && (
                      <span className="text-xs text-gray-500">✓ Done</span>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {filteredReplies.length === 0 && (
          <div className="p-8 text-center text-gray-500">No replies match your filter</div>
        )}
      </div>
    </div>
  );
}
