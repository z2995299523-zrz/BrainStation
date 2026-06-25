import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './pages/Dashboard';
import LearnPage from './pages/LearnPage';
import AdminPage from './pages/AdminPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ExamListPage from './pages/ExamListPage';
import ExamManagePage from './pages/ExamManagePage';
import ExamTakingPage from './pages/ExamTakingPage';
import ExamResultPage from './pages/ExamResultPage';
import UserManagePage from './pages/UserManagePage';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/learn/:subject"
            element={
              <ProtectedRoute>
                <LearnPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/users"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <UserManagePage />
              </ProtectedRoute>
            }
          />
          {/* Exam routes */}
          <Route
            path="/exam"
            element={
              <ProtectedRoute>
                <ExamListPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/exam/manage"
            element={
              <ProtectedRoute allowedRoles={['examiner', 'admin']}>
                <ExamManagePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/exam/take/:examId"
            element={
              <ProtectedRoute>
                <ExamTakingPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/exam/result/:examId"
            element={
              <ProtectedRoute>
                <ExamResultPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;