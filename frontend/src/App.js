import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout, Spin } from 'antd';
import { useAuth } from './contexts/AuthContext';
import api from './services/api';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import AccountsPage from './pages/AccountsPage';
import TweetsPage from './pages/TweetsPage';
import LogsPage from './pages/LogsPage';
import MainLayout from './components/MainLayout';

const { Content } = Layout;

function App() {
  const { isAuthenticated, loading } = useAuth();

  // アプリ起動時にCSRF tokenを取得
  useEffect(() => {
    api.get('/auth/csrf/')
      .catch(err => console.error('CSRF token fetch failed:', err));
  }, []);

  if (loading) {
    return (
      <Layout style={{ minHeight: '100vh', justifyContent: 'center', alignItems: 'center' }}>
        <Content style={{ textAlign: 'center' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>読み込み中...</div>
        </Content>
      </Layout>
    );
  }

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <MainLayout>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/accounts" element={<AccountsPage />} />
        <Route path="/tweets" element={<TweetsPage />} />
        <Route path="/logs" element={<LogsPage />} />
        <Route path="/login" element={<Navigate to="/" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </MainLayout>
  );
}

export default App;