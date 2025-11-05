import React, { useState, useEffect } from 'react';
import { Layout, Menu, Avatar, Dropdown, Button, message, Drawer } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  UserOutlined,
  TwitterOutlined,
  FileTextOutlined,
  LogoutOutlined,
  SettingOutlined,
  MenuOutlined,
} from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';

const { Header, Sider, Content } = Layout;

const MainLayout = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [mobileMenuVisible, setMobileMenuVisible] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  // モバイル判定
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'ダッシュボード',
    },
    {
      key: '/accounts',
      icon: <TwitterOutlined />,
      label: 'アカウント管理',
    },
    {
      key: '/tweets',
      icon: <FileTextOutlined />,
      label: 'ツイート一覧',
    },
    {
      key: '/logs',
      icon: <SettingOutlined />,
      label: '監視ログ',
    },
  ];

  const handleMenuClick = ({ key }) => {
    navigate(key);
    // モバイルの場合はメニューを閉じる
    if (isMobile) {
      setMobileMenuVisible(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      message.success('ログアウトしました');
      navigate('/login');
    } catch (error) {
      message.error('ログアウトに失敗しました');
    }
  };

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'プロフィール',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'ログアウト',
      onClick: handleLogout,
    },
  ];

  // サイドバーのコンテンツ(PC/モバイル共通)
  const sidebarContent = (
    <>
      <div
        style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderBottom: '3px solid #262626',
          background: '#fafafa',
        }}
      >
        <h2 style={{ 
          margin: 0, 
          color: '#1890ff',
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '1px',
          fontSize: (collapsed && !isMobile) ? '16px' : '18px',
        }}>
          {(collapsed && !isMobile) ? 'ASI' : 'Auto Ski Info'}
        </h2>
      </div>
      <Menu
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={handleMenuClick}
        style={{ 
          borderRight: 0,
          fontWeight: 600,
        }}
      />
    </>
  );

  return (
    <Layout className="main-layout">
      {/* PC用サイドバー */}
      {!isMobile && (
        <Sider
          collapsible
          collapsed={collapsed}
          onCollapse={setCollapsed}
          theme="light"
          width={256}
        >
          {sidebarContent}
        </Sider>
      )}

      {/* モバイル用ドロワーメニュー */}
      {isMobile && (
        <Drawer
          placement="left"
          onClose={() => setMobileMenuVisible(false)}
          open={mobileMenuVisible}
          bodyStyle={{ padding: 0 }}
          width={280}
        >
          {sidebarContent}
        </Drawer>
      )}

      <Layout>
        <Header
          style={{
            background: '#fff',
            padding: isMobile ? '0 16px' : '0 24px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            borderBottom: '3px solid #262626',
            boxShadow: '0 4px 0 rgba(0, 0, 0, 0.05)',
          }}
        >
          {/* モバイル用ハンバーガーメニュー */}
          {isMobile && (
            <Button
              type="text"
              icon={<MenuOutlined style={{ fontSize: '20px' }} />}
              onClick={() => setMobileMenuVisible(true)}
              style={{ padding: '4px 8px' }}
            />
          )}
          
          {!isMobile && <div />}
          
          <Dropdown
            menu={{
              items: userMenuItems,
              onClick: ({ key }) => {
                const item = userMenuItems.find(item => item.key === key);
                if (item?.onClick) item.onClick();
              }
            }}
            placement="bottomRight"
          >
            <Button type="text" style={{ display: 'flex', alignItems: 'center' }}>
              <Avatar size="small" icon={<UserOutlined />} />
              {!isMobile && (
                <span style={{ marginLeft: 8 }}>{user?.username || user?.email}</span>
              )}
            </Button>
          </Dropdown>
        </Header>
        <Content className="main-content">
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;