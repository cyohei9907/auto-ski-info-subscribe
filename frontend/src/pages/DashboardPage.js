import React from 'react';
import { Row, Col, Card, Statistic, Typography, Spin, Alert } from 'antd';
import { TwitterOutlined, FileTextOutlined, EyeOutlined, BellOutlined } from '@ant-design/icons';
import { useQuery } from 'react-query';
import { monitorAPI } from '../services/api';

const { Title } = Typography;

const DashboardPage = () => {
  const { data: accounts, isLoading: accountsLoading, error: accountsError } = useQuery(
    'accounts',
    monitorAPI.getAccounts,
    { retry: 1 }
  );

  const { data: tweets, isLoading: tweetsLoading, error: tweetsError } = useQuery(
    'tweets',
    () => monitorAPI.getTweets({ limit: 10 }),
    { retry: 1 }
  );

  const { data: notifications, isLoading: notificationsLoading, error: notificationsError } = useQuery(
    'notifications',
    monitorAPI.getNotifications,
    { retry: 1 }
  );

  const accountsData = Array.isArray(accounts?.data) ? accounts.data : [];
  const tweetsData = Array.isArray(tweets?.data?.results) ? tweets.data.results : (Array.isArray(tweets?.data) ? tweets.data : []);
  const notificationsData = Array.isArray(notifications?.data) ? notifications.data : [];

  const activeAccountsCount = accountsData.filter(account => account.is_active).length;
  const totalTweetsCount = tweetsData.length;
  const unreadNotifications = notificationsData.filter(n => !n.is_read).length;

  if (accountsLoading || tweetsLoading || notificationsLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>データを読み込み中...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <Title level={2} style={{ margin: 0 }}>
          ダッシュボード
        </Title>
        <p style={{ margin: '8px 0 0 0', color: '#666' }}>
          X (Twitter) スキー場情報監視の概要
        </p>
      </div>

      {/* エラー表示 */}
      {(accountsError || tweetsError || notificationsError) && (
        <Alert
          message="データの読み込みに失敗しました"
          description="一部のデータが読み込めませんでした。ページを再読み込みしてください。"
          type="warning"
          closable
          style={{ marginBottom: 16 }}
        />
      )}

      {/* 統計カード */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="監視中アカウント"
              value={activeAccountsCount}
              prefix={<TwitterOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="総アカウント数"
              value={accountsData.length}
              prefix={<EyeOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="最新ツイート"
              value={totalTweetsCount}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="未読通知"
              value={unreadNotifications}
              prefix={<BellOutlined />}
              valueStyle={{ color: unreadNotifications > 0 ? '#ff4d4f' : '#8c8c8c' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* 監視中アカウント */}
        <Col xs={24} lg={12}>
          <Card title="監視中アカウント" style={{ height: '400px' }}>
            {accountsData.length === 0 ? (
              <Alert
                message="監視中のアカウントがありません"
                description="アカウント管理ページから監視したいXアカウントを追加してください。"
                type="info"
                showIcon
              />
            ) : (
              <div style={{ maxHeight: '320px', overflowY: 'auto' }}>
                {accountsData.map((account) => (
                  <Card
                    key={account.id}
                    size="small"
                    style={{ marginBottom: 8 }}
                  >
                    <Card.Meta
                      avatar={
                        account.avatar_url ? (
                          <img
                            src={account.avatar_url}
                            alt={account.username}
                            style={{ width: 32, height: 32, borderRadius: '50%' }}
                          />
                        ) : (
                          <div
                            style={{
                              width: 32,
                              height: 32,
                              borderRadius: '50%',
                              background: '#f0f0f0',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                            }}
                          >
                            <TwitterOutlined />
                          </div>
                        )
                      }
                      title={`@${account.username}`}
                      description={
                        <div>
                          <div>{account.display_name}</div>
                          <div style={{ fontSize: '12px', color: '#8c8c8c' }}>
                            ツイート数: {account.tweets_count || 0}
                          </div>
                        </div>
                      }
                    />
                  </Card>
                ))}
              </div>
            )}
          </Card>
        </Col>

        {/* 最新ツイート */}
        <Col xs={24} lg={12}>
          <Card title="最新ツイート" style={{ height: '400px' }}>
            {tweetsData.length === 0 ? (
              <Alert
                message="最新のツイートがありません"
                description="監視が開始されると、ここに最新のツイートが表示されます。"
                type="info"
                showIcon
              />
            ) : (
              <div style={{ maxHeight: '320px', overflowY: 'auto' }}>
                {tweetsData.slice(0, 5).map((tweet) => (
                  <Card
                    key={tweet.id}
                    size="small"
                    style={{ marginBottom: 8 }}
                  >
                    <div>
                      <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: 4 }}>
                        @{tweet.x_account_username}
                      </div>
                      <div className="tweet-content" style={{ fontSize: '14px' }}>
                        {tweet.content.length > 100
                          ? `${tweet.content.substring(0, 100)}...`
                          : tweet.content
                        }
                      </div>
                      <div className="tweet-meta">
                        {tweet.ai_analysis && (
                          <span className={`sentiment-${tweet.ai_analysis.sentiment}`}>
                            {tweet.ai_analysis.sentiment === 'positive' && '😊'}
                            {tweet.ai_analysis.sentiment === 'negative' && '😞'}
                            {tweet.ai_analysis.sentiment === 'neutral' && '😐'}
                          </span>
                        )}
                        <span style={{ marginLeft: 8 }}>
                          {new Date(tweet.posted_at).toLocaleString('ja-JP')}
                        </span>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardPage;