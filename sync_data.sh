#!/bin/bash
# Sync script to ensure data consistency across Scout Command Center

echo "🔄 Scout Data Sync"
echo "=================="

# Check if dashboard data exists
if [ -f "scout-dashboard-v2/public/scout_data.json" ]; then
    DASHBOARD_COUNT=$(grep -c '"name"' scout-dashboard-v2/public/scout_data.json 2>/dev/null || echo "0")
    echo "✅ Dashboard data: $DASHBOARD_COUNT prospects"
else
    echo "❌ Dashboard data file missing!"
    exit 1
fi

# Check if old root file exists (should be backed up)
if [ -f "scout_data.json" ]; then
    echo "⚠️  Old root file exists — backing up"
    mv scout_data.json "scout_data.json.bak.$(date +%s)"
fi

# Verify state file
if [ -f "scout_state.json" ]; then
    echo "✅ State file present"
else
    echo "⚠️  Creating default state file"
    echo '{}' > scout_state.json
fi

# Verify draft queue
if [ -f "draft_queue.json" ]; then
    DRAFT_COUNT=$(grep -c '"id"' draft_queue.json 2>/dev/null || echo "0")
    echo "✅ Draft queue: $DRAFT_COUNT drafts"
else
    echo "⚠️  No draft queue file"
fi

echo ""
echo "📊 Current Pipeline:"
echo "  • Dashboard file: scout-dashboard-v2/public/scout_data.json"
echo "  • State file: scout_state.json"
echo "  • Draft queue: draft_queue.json"
echo ""
echo "📝 Note: All data updates should write to dashboard file only."
