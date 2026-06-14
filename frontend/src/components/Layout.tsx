import { Link, useLocation } from 'react-router-dom';
import PhonemePanel from './shared/PhonemePanel';

interface LayoutProps {
  children: React.ReactNode;
  streak?: number;
}

export default function Layout({ children, streak = 0 }: LayoutProps) {
  const location = useLocation();

  const navLinks = [
    { to: '/', label: '📊 首页' },
    { to: '/admin', label: '⚙️ 管理' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* 导航栏 */}
      <nav className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link to="/" className="font-bold text-lg text-indigo-600 dark:text-indigo-400">
              🧠 思维训练营
            </Link>
            {navLinks.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`text-sm transition-colors ${
                  location.pathname === link.to
                    ? 'text-indigo-600 font-medium'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <PhonemePanel />
            {streak > 0 && (
              <div className="flex items-center gap-1 text-sm text-orange-500 font-medium">
                🔥 {streak} 天
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* 主内容区 */}
      <main className="max-w-5xl mx-auto px-4 py-8">{children}</main>
    </div>
  );
}
