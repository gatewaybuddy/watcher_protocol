/**
 * Dashboard - Main page for Watcher Protocol
 */

import { useState } from 'react';
import useSWR from 'swr';
import { Activity, AlertTriangle, TrendingUp, Database } from 'lucide-react';

// Fetcher for SWR
const fetcher = (url: string) => fetch(url).then((res) => res.json());

interface Stats {
  total_items: number;
  items_today: number;
  items_this_week: number;
  active_alerts: number;
  categories_breakdown: Record<string, number>;
  risk_levels_breakdown: Record<string, number>;
}

interface Alert {
  id: string;
  rule_name: string;
  item_title: string;
  triggered_at: string;
  acknowledged: boolean;
}

interface RecentItem {
  id: string;
  title: string;
  category: string;
  risk_level: string;
  published_at: string;
  source: string;
}

export default function Dashboard() {
  const [timeRange, setTimeRange] = useState<'day' | 'week' | 'month'>('week');

  // Fetch data
  const { data: stats } = useSWR<Stats>('/api/v1/stats/overview', fetcher, {
    refreshInterval: 60000, // Refresh every minute
  });

  const { data: alertsData } = useSWR<{ alerts: Alert[] }>(
    '/api/v1/alerts?acknowledged=false&limit=10',
    fetcher,
    { refreshInterval: 30000 }
  );

  const { data: itemsData } = useSWR<{ items: RecentItem[] }>(
    `/api/v1/items?risk_level=critical&risk_level=high&limit=20`,
    fetcher,
    { refreshInterval: 60000 }
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">🦇</span>
              <h1 className="text-2xl font-bold text-gray-900">
                Watcher Protocol
              </h1>
            </div>
            <nav className="flex space-x-4">
              <a href="/" className="text-gray-700 hover:text-gray-900 font-medium">
                Dashboard
              </a>
              <a href="/timeline" className="text-gray-500 hover:text-gray-700">
                Timeline
              </a>
              <a href="/search" className="text-gray-500 hover:text-gray-700">
                Search
              </a>
              <a href="/alerts" className="text-gray-500 hover:text-gray-700">
                Alerts
              </a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Total Items"
            value={stats?.total_items || 0}
            icon={<Database className="w-6 h-6" />}
            color="blue"
          />
          <StatsCard
            title="Items This Week"
            value={stats?.items_this_week || 0}
            icon={<TrendingUp className="w-6 h-6" />}
            color="green"
          />
          <StatsCard
            title="Active Alerts"
            value={stats?.active_alerts || 0}
            icon={<AlertTriangle className="w-6 h-6" />}
            color="red"
          />
          <StatsCard
            title="Items Today"
            value={stats?.items_today || 0}
            icon={<Activity className="w-6 h-6" />}
            color="purple"
          />
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Active Alerts */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Active Alerts</h2>
              {alertsData && alertsData.alerts.length > 0 ? (
                <div className="space-y-3">
                  {alertsData.alerts.map((alert) => (
                    <div
                      key={alert.id}
                      className="border-l-4 border-red-500 bg-red-50 p-4 rounded"
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium text-gray-900">
                            {alert.item_title}
                          </p>
                          <p className="text-sm text-gray-600 mt-1">
                            Rule: {alert.rule_name}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            {new Date(alert.triggered_at).toLocaleString()}
                          </p>
                        </div>
                        <button className="text-sm text-blue-600 hover:text-blue-800">
                          Acknowledge
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">
                  No active alerts
                </p>
              )}
            </div>
          </div>

          {/* Category Breakdown */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Categories</h2>
            {stats?.categories_breakdown ? (
              <div className="space-y-3">
                {Object.entries(stats.categories_breakdown).map(
                  ([category, count]) => (
                    <div key={category} className="flex justify-between">
                      <span className="text-gray-700 capitalize">
                        {category}
                      </span>
                      <span className="font-semibold">{count}</span>
                    </div>
                  )
                )}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">Loading...</p>
            )}
          </div>
        </div>

        {/* Recent High-Priority Items */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">
            Recent High-Priority Items
          </h2>
          {itemsData && itemsData.items.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Title
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Category
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Risk
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Source
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Date
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {itemsData.items.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <a
                          href={`/items/${item.id}`}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          {item.title}
                        </a>
                      </td>
                      <td className="px-4 py-3">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {item.category}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <RiskBadge level={item.risk_level} />
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {item.source}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {new Date(item.published_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No items found</p>
          )}
        </div>
      </main>
    </div>
  );
}

// Helper Components

interface StatsCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  color: 'blue' | 'green' | 'red' | 'purple';
}

function StatsCard({ title, value, icon, color }: StatsCardProps) {
  const colors = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    red: 'bg-red-500',
    purple: 'bg-purple-500',
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-3xl font-bold mt-2">{value.toLocaleString()}</p>
        </div>
        <div className={`${colors[color]} p-3 rounded-lg text-white`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

function RiskBadge({ level }: { level: string }) {
  const colors: Record<string, string> = {
    critical: 'bg-red-100 text-red-800',
    high: 'bg-orange-100 text-orange-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-green-100 text-green-800',
    info: 'bg-gray-100 text-gray-800',
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
        colors[level] || colors.info
      }`}
    >
      {level}
    </span>
  );
}
