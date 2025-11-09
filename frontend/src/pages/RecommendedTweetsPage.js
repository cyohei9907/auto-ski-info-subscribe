import React, { useState } from "react";
import {
  Card,
  Table,
  Tag,
  Button,
  Space,
  Select,
  Typography,
  Tooltip,
  Image,
  message,
  Badge,
} from "antd";
import {
  EyeOutlined,
  CheckOutlined,
  ReloadOutlined,
  StarFilled,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "react-query";
import { aiAPI } from "../services/api";

const { Text, Paragraph } = Typography;
const { Option } = Select;

function RecommendedTweetsPage() {
  const [filterRule, setFilterRule] = useState(null);
  const [filterRead, setFilterRead] = useState(null);
  const queryClient = useQueryClient();

  // 获取规则列表（用于筛选）
  const { data: rulesData } = useQuery("aiRules", () =>
    aiAPI.getRules().then((res) => res.data)
  );

  // 确保数据是数组
  const rules = Array.isArray(rulesData) ? rulesData : [];

  // 获取推荐推文
  const { data: tweetsData, isLoading } = useQuery(
    ["recommendedTweets", filterRule, filterRead],
    () => {
      const params = {};
      if (filterRule) params.rule_id = filterRule;
      if (filterRead !== null) params.is_read = filterRead;
      return aiAPI.getRecommendedTweets(params).then((res) => res.data);
    },
    {
      refetchInterval: 30000, // 30秒自动刷新
    }
  );

  // 确保推文数据是数组
  const tweets = Array.isArray(tweetsData) ? tweetsData : [];

  // 标记为已读
  const markReadMutation = useMutation((id) => aiAPI.markRecommendedRead(id), {
    onSuccess: () => {
      message.success("已标记为已读");
      queryClient.invalidateQueries("recommendedTweets");
      queryClient.invalidateQueries("aiRules");
    },
    onError: (error) => {
      message.error(
        `操作失败: ${error.response?.data?.detail || error.message}`
      );
    },
  });

  const handleMarkRead = (id) => {
    markReadMutation.mutate(id);
  };

  const columns = [
    {
      title: "状态",
      dataIndex: "is_read",
      key: "is_read",
      width: 80,
      align: "center",
      render: (isRead) =>
        isRead ? (
          <Tag color="default">已读</Tag>
        ) : (
          <Badge status="processing" text="未读" />
        ),
    },
    {
      title: "相关度",
      dataIndex: "relevance_score",
      key: "relevance_score",
      width: 100,
      align: "center",
      render: (score) => (
        <Tooltip title={`相关度评分: ${score}`}>
          <Tag
            color={score >= 0.8 ? "red" : score >= 0.6 ? "orange" : "blue"}
            icon={<StarFilled />}
          >
            {(score * 100).toFixed(0)}%
          </Tag>
        </Tooltip>
      ),
      sorter: (a, b) => a.relevance_score - b.relevance_score,
    },
    {
      title: "推文内容",
      key: "tweet",
      render: (_, record) => {
        const tweet = record.tweet;
        return (
          <div>
            <Space direction="vertical" size="small" style={{ width: "100%" }}>
              <div>
                <Text strong>@{tweet.account_username}</Text>
                <Text type="secondary" style={{ marginLeft: 8 }}>
                  {new Date(tweet.created_at).toLocaleString("zh-CN")}
                </Text>
              </div>
              <Paragraph ellipsis={{ rows: 3, expandable: true }}>
                {tweet.text}
              </Paragraph>
              {tweet.media_urls && tweet.media_urls.length > 0 && (
                <Image.PreviewGroup>
                  <Space>
                    {tweet.media_urls.slice(0, 4).map((url, idx) => (
                      <Image
                        key={idx}
                        width={60}
                        height={60}
                        src={url}
                        style={{ objectFit: "cover", borderRadius: 4 }}
                      />
                    ))}
                  </Space>
                </Image.PreviewGroup>
              )}
              <Space>
                <Tag>❤️ {tweet.like_count || 0}</Tag>
                <Tag>🔁 {tweet.retweet_count || 0}</Tag>
                <Tag>💬 {tweet.reply_count || 0}</Tag>
              </Space>
            </Space>
          </div>
        );
      },
    },
    {
      title: "应用规则",
      dataIndex: "prompt_rule_name",
      key: "prompt_rule_name",
      width: 150,
      ellipsis: true,
      render: (name) => <Tag color="purple">{name}</Tag>,
    },
    {
      title: "AI推荐理由",
      dataIndex: "ai_reason",
      key: "ai_reason",
      width: 250,
      ellipsis: true,
      render: (reason) => (
        <Tooltip title={reason}>
          <Paragraph
            ellipsis={{ rows: 2 }}
            style={{ marginBottom: 0, fontSize: 13 }}
          >
            {reason}
          </Paragraph>
        </Tooltip>
      ),
    },
    {
      title: "推荐时间",
      dataIndex: "created_at",
      key: "created_at",
      width: 180,
      render: (date) => new Date(date).toLocaleString("zh-CN"),
      sorter: (a, b) => new Date(a.created_at) - new Date(b.created_at),
    },
    {
      title: "操作",
      key: "actions",
      width: 120,
      fixed: "right",
      render: (_, record) => (
        <Space>
          {!record.is_read && (
            <Button
              type="primary"
              size="small"
              icon={<CheckOutlined />}
              onClick={() => handleMarkRead(record.id)}
              loading={markReadMutation.isLoading}
            >
              标记已读
            </Button>
          )}
          {record.tweet.tweet_url && (
            <Tooltip title="在Twitter上查看">
              <Button
                size="small"
                icon={<EyeOutlined />}
                onClick={() => window.open(record.tweet.tweet_url, "_blank")}
              >
                查看
              </Button>
            </Tooltip>
          )}
        </Space>
      ),
    },
  ];

  // 统计信息
  const stats = {
    total: tweets.length,
    unread: tweets.filter((t) => !t.is_read).length,
    highRelevance: tweets.filter((t) => t.relevance_score >= 0.8).length,
  };

  return (
    <div style={{ padding: "24px" }}>
      <Card
        title={
          <Space>
            <span>AI推荐推文</span>
            <Badge count={stats.unread} style={{ backgroundColor: "#52c41a" }}>
              <Tag color="default">未读</Tag>
            </Badge>
          </Space>
        }
        extra={
          <Space>
            <Select
              placeholder="选择规则"
              style={{ width: 200 }}
              allowClear
              value={filterRule}
              onChange={setFilterRule}
            >
              {rules.map((rule) => (
                <Option key={rule.id} value={rule.id}>
                  {rule.name}
                </Option>
              ))}
            </Select>
            <Select
              placeholder="阅读状态"
              style={{ width: 120 }}
              allowClear
              value={filterRead}
              onChange={setFilterRead}
            >
              <Option value={false}>未读</Option>
              <Option value={true}>已读</Option>
            </Select>
            <Button
              icon={<ReloadOutlined />}
              onClick={() => queryClient.invalidateQueries("recommendedTweets")}
            >
              刷新
            </Button>
          </Space>
        }
      >
        <Space
          style={{ marginBottom: 16, width: "100%", justifyContent: "center" }}
        >
          <Card size="small" style={{ width: 150 }}>
            <div style={{ textAlign: "center" }}>
              <div
                style={{ fontSize: 24, fontWeight: "bold", color: "#1890ff" }}
              >
                {stats.total}
              </div>
              <div style={{ color: "#999" }}>总推荐数</div>
            </div>
          </Card>
          <Card size="small" style={{ width: 150 }}>
            <div style={{ textAlign: "center" }}>
              <div
                style={{ fontSize: 24, fontWeight: "bold", color: "#52c41a" }}
              >
                {stats.unread}
              </div>
              <div style={{ color: "#999" }}>未读推文</div>
            </div>
          </Card>
          <Card size="small" style={{ width: 150 }}>
            <div style={{ textAlign: "center" }}>
              <div
                style={{ fontSize: 24, fontWeight: "bold", color: "#ff4d4f" }}
              >
                {stats.highRelevance}
              </div>
              <div style={{ color: "#999" }}>高相关度</div>
            </div>
          </Card>
        </Space>

        <Table
          dataSource={tweets}
          columns={columns}
          rowKey="id"
          loading={isLoading}
          scroll={{ x: 1400 }}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条推荐`,
          }}
          rowClassName={(record) => (!record.is_read ? "unread-row" : "")}
        />
      </Card>

      <style>{`
        .unread-row {
          background-color: #f0f9ff;
        }
      `}</style>
    </div>
  );
}

export default RecommendedTweetsPage;
