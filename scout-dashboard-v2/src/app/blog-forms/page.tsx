"use client";

import { useEffect, useState } from "react";

interface BlogForm {
  id?: string;
  name: string;
  url: string;
  contactUrl?: string;
  message: string;
  status: 'pending' | 'auto_submitted' | 'manual_needed' | 'completed';
  city?: string;
  branch: string;
  submittedAt?: string;
}

const DEFAULT_MESSAGE = `Hi there,

My name is Keri Erten, and I'm a pianist, music teacher, and co-founder of Thoven — an all-in-one music education platform where families can find verified, background-checked teachers trained at top schools like The Juilliard School.

I've been reading your blog and love the way you connect with your audience. I noticed your recent post about [TOPIC] really resonated with me.

I wanted to reach out about a potential partnership opportunity. Thoven helps families find credentialed music teachers for live private lessons, with everything from scheduling to progress tracking built into one platform.

For homeschool families in Arizona, Thoven is also ESA-eligible through ClassWallet.

Would you be open to exploring a collaboration? I'd love to discuss:
• Affiliate partnership opportunities
• Complimentary lessons for your family to experience the platform
• Any other structure that works best for you and your readers

Looking forward to connecting!

Keri Erten
Co-Founder & CXO, Thoven
keri@thoven.co`;

const SAMPLE_BLOGS: BlogForm[] = [
  {
    name: "Miami Mom Collective",
    url: "https://miamimomcollective.com",
    contactUrl: "https://miamimomcollective.com/contact",
    message: DEFAULT_MESSAGE.replace('[TOPIC]', 'family activities in Miami'),
    status: 'pending',
    city: 'Miami',
    branch: 'Mom Blogs'
  },
  {
    name: "LA Parent Magazine",
    url: "https://laparent.com",
    contactUrl: "https://laparent.com/contact-us",
    message: DEFAULT_MESSAGE.replace('[TOPIC]', 'educational resources'),
    status: 'manual_needed',
    city: 'LA',
    branch: 'Mom Blogs'
  }
];

function BlogFormCard({ 
  form, 
  onUpdate 
}: { 
  form: BlogForm; 
  onUpdate: (updated: BlogForm) => void;
}) {
  const [copied, setCopied] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const statusColors: Record<BlogForm['status'], string> = {
    'pending': 'bg-yellow-900 text-yellow-300',
    'auto_submitted': 'bg-green-900 text-green-300',
    'manual_needed': 'bg-red-900 text-red-300',
    'completed': 'bg-blue-900 text-blue-300'
  };

  const statusLabels: Record<BlogForm['status'], string> = {
    'pending': '🟡 Pending',
    'auto_submitted': '✅ Auto-Submitted',
    'manual_needed': '📝 Manual Needed',
    'completed': '✓ Completed'
  };

  async function handleAutoSubmit() {
    setIsSubmitting(true);
    
    // Simulate auto-submit attempt
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // For demo, randomly succeed or fail
    const success = Math.random() > 0.3;
    
    if (success) {
      onUpdate({
        ...form,
        status: 'auto_submitted',
        submittedAt: new Date().toISOString()
      });
    } else {
      onUpdate({
        ...form,
        status: 'manual_needed'
      });
    }
    
    setIsSubmitting(false);
  }

  function copyMessage() {
    navigator.clipboard.writeText(form.message);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function openContactForm() {
    window.open(form.contactUrl || form.url, '_blank');
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h3 className="font-semibold text-lg">{form.name}</h3>
            <span className={`text-xs px-2 py-1 rounded-full ${statusColors[form.status]}`}>
              {statusLabels[form.status]}
            </span>
          </div>
          <p className="text-gray-400 text-sm">{form.city} • {form.branch}</p>
          <a 
            href={form.url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-400 text-xs hover:underline"
          >
            {form.url}
          </a>
        </div>
        <div className="flex gap-2">
          {form.status === 'pending' && (
            <button
              onClick={handleAutoSubmit}
              disabled={isSubmitting}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 rounded-lg text-sm font-medium transition"
            >
              {isSubmitting ? 'Trying...' : 'Auto-Submit'}
            </button>
          )}
          <button
            onClick={copyMessage}
            className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition"
          >
            {copied ? 'Copied!' : 'Copy Message'}
          </button>
          
          <button
            onClick={openContactForm}
            className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition"
          >
            Open Form
          </button>
          
          {form.status === 'manual_needed' && (
            <button
              onClick={() => onUpdate({ ...form, status: 'completed', submittedAt: new Date().toISOString() })}
              className="px-4 py-2 bg-green-600 hover:bg-green-500 rounded-lg text-sm font-medium transition"
            >
              Mark Done
            </button>
          )}
        </div>
      </div>

      <div className="bg-gray-950 rounded-lg border border-gray-800 p-4">
        <p className="text-xs text-gray-500 mb-2">Pre-written message:</p>
        <pre className="text-xs text-gray-300 whitespace-pre-wrap font-mono max-h-32 overflow-y-auto">
          {form.message}
        </pre>
      </div>

      {form.submittedAt && (
        <p className="text-xs text-gray-500 mt-3">
          Submitted: {new Date(form.submittedAt).toLocaleDateString()}
        </p>
      )}
    </div>
  );
}

export default function BlogForms() {
  const [blogs, setBlogs] = useState<BlogForm[]>(SAMPLE_BLOGS);
  const [filter, setFilter] = useState<'All' | BlogForm['status']>('All');
  const [newBlogOpen, setNewBlogOpen] = useState(false);
  const [newBlog, setNewBlog] = useState<Partial<BlogForm>>({
    status: 'pending',
    branch: 'Mom Blogs',
    message: DEFAULT_MESSAGE
  });

  const filteredBlogs = filter === 'All' 
    ? blogs 
    : blogs.filter(b => b.status === filter);

  const statusCounts = blogs.reduce((acc, b) => {
    acc[b.status] = (acc[b.status] || 0) + 1;
    return acc;
  }, {} as Record<BlogForm['status'], number>);

  function handleUpdate(updated: BlogForm) {
    setBlogs(blogs.map(b => b.name === updated.name ? updated : b));
  }

  function handleAddNew() {
    if (newBlog.name && newBlog.url) {
      setBlogs([...blogs, newBlog as BlogForm]);
      setNewBlogOpen(false);
      setNewBlog({
        status: 'pending',
        branch: 'Mom Blogs',
        message: DEFAULT_MESSAGE
      });
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Blog Forms</h1>
          <p className="text-gray-400">Manage blog contact form submissions</p>
        </div>
        <button
          onClick={() => setNewBlogOpen(!newBlogOpen)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium transition"
        >
          {newBlogOpen ? 'Cancel' : '+ Add Blog'}
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {(['pending', 'auto_submitted', 'manual_needed', 'completed'] as const).map(status => (
          <button
            key={status}
            onClick={() => setFilter(filter === status ? 'All' : status)}
            className={`bg-gray-900 border rounded-xl p-4 text-center transition ${
              filter === status ? 'border-blue-500' : 'border-gray-800'
            }`}
          >
            <p className="text-2xl font-bold text-blue-400">{statusCounts[status] || 0}</p>
            <p className="text-xs text-gray-500 capitalize">{status.replace('_', ' ')}</p>
          </button>
        ))}
      </div>

      {/* Add New Blog Form */}
      {newBlogOpen && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h3 className="font-semibold mb-4">Add New Blog</h3>
          <div className="grid grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Blog name"
              value={newBlog.name || ''}
              onChange={(e) => setNewBlog({...newBlog, name: e.target.value})}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2"
            />
            <input
              type="text"
              placeholder="Blog URL"
              value={newBlog.url || ''}
              onChange={(e) => setNewBlog({...newBlog, url: e.target.value})}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2"
            />
            <input
              type="text"
              placeholder="Contact form URL (optional)"
              value={newBlog.contactUrl || ''}
              onChange={(e) => setNewBlog({...newBlog, contactUrl: e.target.value})}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2"
            />
            <select
              value={newBlog.branch}
              onChange={(e) => setNewBlog({...newBlog, branch: e.target.value})}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2"
            >
              <option>Mom Blogs</option>
              <option>Homeschool Blogs (AZ)</option>
            </select>
          </div>
          <div className="mt-4 flex justify-end">
            <button
              onClick={handleAddNew}
              className="px-4 py-2 bg-green-600 hover:bg-green-500 rounded-lg text-sm font-medium"
            >
              Add Blog
            </button>
          </div>
        </div>
      )}

      {/* Blog Forms List */}
      <div className="space-y-4">
        {filteredBlogs.map((blog, i) => (
          <BlogFormCard 
            key={i} 
            form={blog} 
            onUpdate={handleUpdate}
          />
        ))}
      </div>

      {filteredBlogs.length === 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center">
          <p className="text-gray-400">No blogs found with this filter.</p>
        </div>
      )}
    </div>
  );
}
