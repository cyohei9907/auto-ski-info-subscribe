import React, { useState } from 'react';
import {
  Card,
  Button,
  List,
  Space,
  Tag,
  Typography,
  Select,
  Input,
  Row,
  Col,
  Slider,
  message,
  Avatar,
  Tooltip,
} from 'antd';
import {
  TwitterOutlined,
  HeartOutlined,
  RetweetOutlined,
  MessageOutlined,
  ReloadOutlined,
  RobotOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { monitorAPI } from '../services/api';

const { Title, Text, Paragraph } = Typography;
const { Search } = Input;
const { Option } = Select;

const TweetsPage = () => {
  const [filters, setFilters] = useState({
    account_id: undefined,
    sentiment: undefined,
    min_importance: 0,
    search: '',
  });
  
  const queryClient = useQueryClient();

  const { data: accounts } = useQuery('accounts', monitorAPI.getAccounts);
  const { data: tweets, isLoading } = useQuery(
    ['tweets', filters],
    () => monitorAPI.getTweets(filters),
    {
      keepPreviousData: true,
    }
  );

  const analyzeTweetMutation = useMutation(monitorAPI.analyzeTweet, {
    onSuccess: () => {
      message.success('AI分析が完了しました');
      queryClient.invalidateQueries(['tweets', filters]);
    },
    onError: () => {
      message.error('AI分析に失敗しました');
    },
  });

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleAnalyzeTweet = (tweetId) => {
    analyzeTweetMutation.mutate(tweetId);
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive': return 'green';
      case 'negative': return 'red';
      case 'neutral': return 'default';
      default: return 'default';
    }
  };

  const getSentimentText = (sentiment) => {
    switch (sentiment) {
      case 'positive': return 'ポジティブ';
      case 'negative': return 'ネガティブ';
      case 'neutral': return 'ニュートラル';
      default: return '未分析';
    }
  };

  const getImportanceClass = (score) => {
    if (score >= 0.7) return 'importance-high';
    if (score >= 0.4) return 'importance-medium';
    return 'importance-low';
  };

  const tweetsData = Array.isArray(tweets?.data?.results) ? tweets.data.results : (Array.isArray(tweets?.data) ? tweets.data : []);
  const accountsData = Array.isArray(accounts?.data) ? accounts.data : [];

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Title level={2} style={{ margin: 0 }}>
              ツイート一覧
            </Title>
            <p style={{ margin: '8px 0 0 0', color: '#666' }}>
              監視中のアカウントから取得したツイートとAI分析結果
            </p>
          </div>
          <Button
            icon={<ReloadOutlined />}
            onClick={() => queryClient.invalidateQueries(['tweets', filters])}
            loading={isLoading}
          >
            更新
          </Button>
        </div>
      </div>

      {/* フィルター */}
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={6}>
            <label>アカウント</label>
            <Select
              style={{ width: '100%' }}
              placeholder="すべてのアカウント"
              allowClear
              value={filters.account_id}
              onChange={(value) => handleFilterChange('account_id', value)}
            >
              {accountsData.map(account => (
                <Option key={account.id} value={account.id}>
                  @{account.username}
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <label>感情</label>
            <Select
              style={{ width: '100%' }}
              placeholder="すべての感情"
              allowClear
              value={filters.sentiment}
              onChange={(value) => handleFilterChange('sentiment', value)}
            >
              <Option value="positive">ポジティブ</Option>
              <Option value="negative">ネガティブ</Option>
              <Option value="neutral">ニュートラル</Option>
            </Select>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <label>重要度 (最小値: {filters.min_importance})</label>
            <Slider
              min={0}
              max={1}
              step={0.1}
              value={filters.min_importance}
              onChange={(value) => handleFilterChange('min_importance', value)}
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <label>検索</label>
            <Search
              placeholder="ツイート内容を検索"
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              allowClear
            />
          </Col>
        </Row>
      </Card>

      {/* ツイート一覧 */}
      <Card>
        <List
          itemLayout="vertical"
          size="large"
          dataSource={tweetsData}
          loading={isLoading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} / ${total} 件`,
          }}
          renderItem={(tweet) => (
            <List.Item
              key={tweet.id}
              className={`tweet-card ${tweet.ai_analysis ? getImportanceClass(tweet.ai_analysis.importance_score) : ''}`}
              actions={[
                <Space key="stats">
                  <span><HeartOutlined /> {tweet.like_count}</span>
                  <span><RetweetOutlined /> {tweet.retweet_count}</span>
                  <span><MessageOutlined /> {tweet.reply_count}</span>
                </Space>,
                !tweet.ai_analysis ? (
                  <Button
                    key="analyze"
                    type="text"
                    icon={<RobotOutlined />}
                    onClick={() => handleAnalyzeTweet(tweet.id)}
                    loading={analyzeTweetMutation.isLoading}
                  >
                    AI分析
                  </Button>
                ) : null,
              ].filter(Boolean)}
            >
              <List.Item.Meta
                avatar={
                  <Avatar icon={<TwitterOutlined />} />
                }
                title={
                  <Space>
                    <Text strong>@{tweet.x_account_username}</Text>
                    {tweet.ai_analysis && (
                      <>
                        <Tag color={getSentimentColor(tweet.ai_analysis.sentiment)}>
                          {getSentimentText(tweet.ai_analysis.sentiment)}
                        </Tag>
                        <Tooltip title={`重要度: ${Math.round(tweet.ai_analysis.importance_score * 100)}%`}>
                          <Tag color="blue">
                            重要度: {Math.round(tweet.ai_analysis.importance_score * 100)}%
                          </Tag>
                        </Tooltip>
                      </>
                    )}
                  </Space>
                }
                description={
                  <Text type="secondary">
                    {new Date(tweet.posted_at).toLocaleString('ja-JP')}
                  </Text>
                }
              />
              
              <div className="tweet-content">
                <Paragraph>{tweet.content}</Paragraph>
              </div>

              {/* AI分析結果 */}
              {tweet.ai_analysis && (
                <Card size="small" style={{ marginTop: 16, background: '#fafafa' }}>
                  <Row gutter={16}>
                    <Col span={12}>
                      <Text strong>AI要約:</Text>
                      <div style={{ marginTop: 4 }}>
                        <Text>{tweet.ai_analysis.summary}</Text>
                      </div>
                    </Col>
                    <Col span={12}>
                      <Text strong>抽出トピック:</Text>
                      <div style={{ marginTop: 4 }}>
                        {tweet.ai_analysis.topics.map((topic, index) => (
                          <Tag key={index} style={{ marginBottom: 4 }}>
                            {topic}
                          </Tag>
                        ))}
                      </div>
                    </Col>
                  </Row>
                </Card>
              )}

              {/* ハッシュタグ */}
              {tweet.hashtags.length > 0 && (
                <div style={{ marginTop: 8 }}>
                  {tweet.hashtags.map((hashtag, index) => (
                    <Tag key={index} color="blue">
                      #{hashtag}
                    </Tag>
                  ))}
                </div>
              )}
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
};

export default TweetsPage;