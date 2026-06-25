import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import PhonemePanel from './shared/PhonemePanel';
import { Button } from './ui/button';
import { Toaster } from './ui/sonner';
import { TooltipProvider } from './ui/tooltip';

interface LayoutProps {
  children: React.ReactNode;
  streak?: number;
}

export default function Layout({ children, streak = 0 }: LayoutProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const token = useAuthStore((s) => s.token);
  const logout = useAuthStore((s) => s.logout);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isAuthPage = location.pathname === '/login' || location.pathname === '/register';

  const role = user?.role || 'learner';

  const navLinks = [
    { to: '/', label: '📊 首页' },
  ];

  if (role === 'admin') {
    navLinks.push({ to: '/admin', label: '⚙️ 管理' });
    navLinks.push({ to: '/admin/users', label: '👥 用户管理' });
  }

  if (role === 'examiner' || role === 'admin') {
    navLinks.push({ to: '/exam/manage', label: '📝 考试管理' });
  }

  // All authenticated users can see exam list
  navLinks.push({ to: '/exam', label: '📋 综合考试' });

  return (
    <div className="min-h-screen bg-background">
      {/* 导航栏 */}
      <nav className="border-b border-border bg-card sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to="/" className="font-bold text-lg bg-gradient-to-r from-indigo-600 to-emerald-500 bg-clip-text text-transparent">
              🧠 思维训练营
            </Link>
            {token && navLinks.map((link) => (
              <Button
                key={link.to}
                variant="ghost"
                size="sm"
                asChild
                className={location.pathname === link.to ? 'text-primary font-medium' : 'text-muted-foreground'}
              >
                <Link to={link.to}>{link.label}</Link>
              </Button>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <PhonemePanel />
            {token && user && (
              <>
                <span className="text-sm text-muted-foreground">
                  👤 {user.username}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  className="text-muted-foreground hover:text-red-500"
                >
                  退出
                </Button>
              </>
            )}
            {!token && !isAuthPage && (
              <Link
                to="/login"
                className="text-sm text-primary hover:text-primary/80 font-medium"
              >
                登录
              </Link>
            )}
            {streak > 0 && (
              <div className="flex items-center gap-1 text-sm text-orange-500 font-medium">
                🔥 {streak} 天
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* 主内容区 */}
      <main className="max-w-5xl mx-auto px-4 py-8">
        <TooltipProvider delayDuration={300}>
          {children}
        </TooltipProvider>
      </main>

      {/* Toast 通知 */}
      <Toaster />
    </div>
  );
}
