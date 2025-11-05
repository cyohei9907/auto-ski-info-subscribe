import React, { useState } from 'react';
import { Card, Form, Input, Button, Alert, Typography, Row, Col, Divider } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, TwitterOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';

const { Title, Text } = Typography;

const LoginPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login, register } = useAuth();

  const onFinish = async (values) => {
    setLoading(true);
    setError('');

    try {
      const result = isLogin ? await login(values) : await register(values);
      
      if (!result.success) {
        setError(result.error);
      }
    } catch (error) {
      setError('予期しないエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setError('');
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: '#f5f5f5',
        backgroundImage: `
          linear-gradient(90deg, #e0e0e0 1px, transparent 1px),
          linear-gradient(#e0e0e0 1px, transparent 1px)
        `,
        backgroundSize: '20px 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
        position: 'relative',
      }}
    >
      {/* Wireframe装飾 */}
      <div style={{
        position: 'absolute',
        top: '20px',
        left: '20px',
        width: '100px',
        height: '100px',
        border: '3px solid #1890ff',
        borderRadius: '50%',
        opacity: 0.3,
      }} />
      <div style={{
        position: 'absolute',
        bottom: '40px',
        right: '40px',
        width: '150px',
        height: '150px',
        border: '3px solid #52c41a',
        opacity: 0.3,
      }} />

      <Row justify="center" style={{ width: '100%', maxWidth: '1200px' }}>
        <Col xs={24} sm={20} md={16} lg={14} xl={10}>
          <Card
            style={{
              background: 'white',
              border: '3px solid #262626',
              borderRadius: '0',
              boxShadow: '8px 8px 0 rgba(0, 0, 0, 0.1)',
              position: 'relative',
            }}
            bodyStyle={{ padding: '48px' }}
          >
            {/* ヘッダーセクション */}
            <div style={{ textAlign: 'center', marginBottom: '40px' }}>
              <div style={{
                width: '80px',
                height: '80px',
                border: '3px solid #1890ff',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 20px',
                background: '#e6f7ff',
              }}>
                <TwitterOutlined style={{ fontSize: '36px', color: '#1890ff' }} />
              </div>
              <Title level={2} style={{ 
                color: '#262626', 
                marginBottom: '8px',
                fontWeight: 700,
                letterSpacing: '-0.5px',
              }}>
                Auto Ski Info Subscribe
              </Title>
              <Text style={{ 
                fontSize: '14px', 
                color: '#8c8c8c',
                display: 'block',
                marginBottom: '8px',
              }}>
                X (Twitter) スキー場情報監視システム
              </Text>
              <Divider style={{ margin: '24px 0', borderColor: '#d9d9d9' }} />
              <Text strong style={{ 
                fontSize: '18px', 
                color: '#262626',
                display: 'block',
              }}>
                {isLogin ? 'ログイン' : '新規登録'}
              </Text>
            </div>

            {error && (
              <Alert
                message={error}
                type="error"
                style={{ 
                  marginBottom: '24px',
                  border: '2px solid #ff4d4f',
                  borderRadius: '0',
                  background: '#fff2f0',
                }}
                showIcon
              />
            )}

            <Form
              name={isLogin ? 'login' : 'register'}
              onFinish={onFinish}
              layout="vertical"
              size="large"
            >
              <Form.Item
                name="email"
                label={
                  <span style={{ 
                    fontSize: '14px', 
                    fontWeight: 600, 
                    color: '#262626',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                  }}>
                    {isLogin ? "メールアドレス / ユーザー名" : "メールアドレス"}
                  </span>
                }
                rules={[
                  { required: true, message: isLogin ? 'メールアドレスまたはユーザー名を入力してください' : 'メールアドレスを入力してください' },
                  isLogin ? {} : { type: 'email', message: '有効なメールアドレスを入力してください' },
                ]}
              >
                <Input 
                  prefix={isLogin ? <UserOutlined style={{ color: '#8c8c8c' }} /> : <MailOutlined style={{ color: '#8c8c8c' }} />}
                  placeholder={isLogin ? "admin または admin@example.com" : "your-email@example.com"}
                  style={{
                    border: '2px solid #d9d9d9',
                    borderRadius: '0',
                    height: '48px',
                    fontSize: '15px',
                  }}
                />
              </Form.Item>

              {!isLogin && (
                <Form.Item
                  name="username"
                  label={
                    <span style={{ 
                      fontSize: '14px', 
                      fontWeight: 600, 
                      color: '#262626',
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px',
                    }}>
                      ユーザー名
                    </span>
                  }
                  rules={[
                    { required: true, message: 'ユーザー名を入力してください' },
                    { min: 3, message: 'ユーザー名は3文字以上である必要があります' },
                  ]}
                >
                  <Input 
                    prefix={<UserOutlined style={{ color: '#8c8c8c' }} />}
                    placeholder="username"
                    style={{
                      border: '2px solid #d9d9d9',
                      borderRadius: '0',
                      height: '48px',
                      fontSize: '15px',
                    }}
                  />
                </Form.Item>
              )}

              <Form.Item
                name="password"
                label={
                  <span style={{ 
                    fontSize: '14px', 
                    fontWeight: 600, 
                    color: '#262626',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                  }}>
                    パスワード
                  </span>
                }
                rules={[
                  { required: true, message: 'パスワードを入力してください' },
                  { min: 8, message: 'パスワードは8文字以上である必要があります' },
                ]}
              >
                <Input.Password
                  prefix={<LockOutlined style={{ color: '#8c8c8c' }} />}
                  placeholder="••••••••"
                  style={{
                    border: '2px solid #d9d9d9',
                    borderRadius: '0',
                    height: '48px',
                    fontSize: '15px',
                  }}
                />
              </Form.Item>

              {!isLogin && (
                <Form.Item
                  name="password_confirm"
                  label={
                    <span style={{ 
                      fontSize: '14px', 
                      fontWeight: 600, 
                      color: '#262626',
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px',
                    }}>
                      パスワード確認
                    </span>
                  }
                  dependencies={['password']}
                  rules={[
                    { required: true, message: 'パスワードを再入力してください' },
                    ({ getFieldValue }) => ({
                      validator(_, value) {
                        if (!value || getFieldValue('password') === value) {
                          return Promise.resolve();
                        }
                        return Promise.reject(new Error('パスワードが一致しません'));
                      },
                    }),
                  ]}
                >
                  <Input.Password
                    prefix={<LockOutlined style={{ color: '#8c8c8c' }} />}
                    placeholder="••••••••"
                    style={{
                      border: '2px solid #d9d9d9',
                      borderRadius: '0',
                      height: '48px',
                      fontSize: '15px',
                    }}
                  />
                </Form.Item>
              )}

              <Form.Item style={{ marginTop: '32px', marginBottom: '24px' }}>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                  block
                  style={{ 
                    height: '56px', 
                    fontSize: '16px',
                    fontWeight: 600,
                    border: '3px solid #1890ff',
                    borderRadius: '0',
                    background: '#1890ff',
                    color: 'white',
                    boxShadow: '4px 4px 0 rgba(24, 144, 255, 0.2)',
                    transition: 'all 0.3s',
                    textTransform: 'uppercase',
                    letterSpacing: '1px',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translate(-2px, -2px)';
                    e.currentTarget.style.boxShadow = '6px 6px 0 rgba(24, 144, 255, 0.3)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translate(0, 0)';
                    e.currentTarget.style.boxShadow = '4px 4px 0 rgba(24, 144, 255, 0.2)';
                  }}
                >
                  {isLogin ? 'ログイン' : '新規登録'}
                </Button>
              </Form.Item>
            </Form>

            <Divider style={{ borderColor: '#d9d9d9' }} />

            <div style={{ textAlign: 'center' }}>
              <Text style={{ color: '#8c8c8c', fontSize: '14px' }}>
                {isLogin ? 'アカウントをお持ちでない方は' : '既にアカウントをお持ちの方は'}
              </Text>
              <Button 
                type="link" 
                onClick={toggleMode}
                style={{
                  color: '#1890ff',
                  fontWeight: 600,
                  fontSize: '14px',
                  padding: '0 8px',
                  textDecoration: 'underline',
                }}
              >
                {isLogin ? '新規登録' : 'ログイン'}
              </Button>
            </div>

            {/* デフォルトログイン情報 */}
            {isLogin && (
              <div style={{
                marginTop: '24px',
                padding: '16px',
                background: '#f0f0f0',
                border: '2px dashed #d9d9d9',
              }}>
                <Text style={{ 
                  fontSize: '12px', 
                  color: '#8c8c8c',
                  display: 'block',
                  marginBottom: '8px',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                }}>
                  デフォルトログイン情報
                </Text>
                <div style={{ fontSize: '13px', color: '#595959' }}>
                  <div style={{ marginBottom: '4px' }}>
                    <Text strong>ユーザー名:</Text> <Text code>admin</Text>
                  </div>
                  <div>
                    <Text strong>パスワード:</Text> <Text code>admin@123</Text>
                  </div>
                </div>
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default LoginPage;