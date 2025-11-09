import React from "react";
import {
  Card,
  Avatar,
  Typography,
  Space,
  Tag,
  Image,
  Row,
  Col,
  Button,
  Popconfirm,
  message,
} from "antd";
import {
  HeartOutlined,
  RetweetOutlined,
  MessageOutlined,
  LinkOutlined,
  DeleteOutlined,
} from "@ant-design/icons";
import { monitorAPI } from "../services/api";
import "./TweetCard.css";

const { Text, Paragraph } = Typography;

// X (Twitter) 图标组件
const XIcon = ({ style }) => (
  <svg
    viewBox="0 0 24 24"
    style={{ width: "1em", height: "1em", fill: "currentColor", ...style }}
  >
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
  </svg>
);

const TweetCard = ({ tweet, onLike, onDelete }) => {
  const {
    id,
    tweet_id,
    content,
    x_account_username,
    x_account_display_name,
    x_account_avatar,
    posted_at,
    retweet_count,
    like_count,
    reply_count,
    media_urls,
    ai_relevant,
    ai_summary,
    tweet_url,
  } = tweet;

  const handleDelete = async () => {
    try {
      await monitorAPI.deleteTweet(id);
      message.success("推文已删除");
      if (onDelete) {
        onDelete(id);
      }
    } catch (error) {
      message.error(
        "删除失败: " + (error.response?.data?.message || error.message)
      );
    }
  };

  // 格式化时间显示
  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "刚刚";
    if (diffMins < 60) return `${diffMins}分钟前`;
    if (diffHours < 24) return `${diffHours}小时前`;
    if (diffDays < 7) return `${diffDays}天前`;

    return date.toLocaleDateString("zh-CN", {
      month: "short",
      day: "numeric",
      year: date.getFullYear() !== now.getFullYear() ? "numeric" : undefined,
    });
  };

  // 格式化数字显示 (1000+ -> 1K)
  const formatCount = (count) => {
    if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
    if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
    return count;
  };

  // 渲染推文内容,支持 hashtag 和 mention 高亮
  const renderContent = (text) => {
    if (!text) return null;

    const parts = text.split(/(\s+|#\w+|@\w+)/g);
    return parts.map((part, index) => {
      if (part.startsWith("#")) {
        return (
          <span key={index} style={{ color: "#1890ff", cursor: "pointer" }}>
            {part}
          </span>
        );
      } else if (part.startsWith("@")) {
        return (
          <span key={index} style={{ color: "#1890ff", cursor: "pointer" }}>
            {part}
          </span>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  return (
    <Card
      className="tweet-card"
      style={{
        marginBottom: "16px",
        borderRadius: "16px",
        border: "1px solid #e1e8ed",
        boxShadow: "none",
      }}
      styles={{
        body: { padding: "16px" },
      }}
      hoverable
    >
      {/* 头部: 头像 + 用户信息 + X logo */}
      <Space align="start" style={{ width: "100%", marginBottom: "12px" }}>
        <Avatar size={48} src={x_account_avatar} style={{ flexShrink: 0 }}>
          {x_account_display_name?.[0] || x_account_username[0].toUpperCase()}
        </Avatar>

        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
            <Text strong style={{ fontSize: "15px" }}>
              {x_account_display_name || x_account_username}
            </Text>
            <XIcon style={{ fontSize: "14px", color: "#1890ff" }} />
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <Text type="secondary" style={{ fontSize: "14px" }}>
              @{x_account_username}
            </Text>
            <Text type="secondary" style={{ fontSize: "14px" }}>
              ·
            </Text>
            <Text type="secondary" style={{ fontSize: "14px" }}>
              {formatTime(posted_at)}
            </Text>
          </div>
        </div>
      </Space>

      {/* AI 相关性标签 */}
      {ai_relevant && (
        <Tag color="gold" style={{ marginBottom: "12px" }}>
          ⭐ AI 推荐
        </Tag>
      )}

      {/* 推文内容 */}
      <Paragraph
        style={{
          fontSize: "15px",
          lineHeight: "20px",
          marginBottom: media_urls?.length > 0 ? "12px" : "16px",
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
        }}
      >
        {renderContent(content)}
      </Paragraph>

      {/* AI 摘要 */}
      {ai_summary && (
        <Card
          size="small"
          style={{
            backgroundColor: "#f7f9fa",
            border: "1px solid #e1e8ed",
            borderRadius: "8px",
            marginBottom: "12px",
          }}
        >
          <Text type="secondary" style={{ fontSize: "13px" }}>
            🤖 AI 摘要: {ai_summary}
          </Text>
        </Card>
      )}

      {/* 媒体图片 */}
      {media_urls && media_urls.length > 0 && (
        <div style={{ marginBottom: "12px" }}>
          <Row gutter={[8, 8]}>
            {media_urls.slice(0, 4).map((url, index) => {
              // 根据图片数量决定布局
              let colSpan = 24;
              let maxHeight = "400px";

              if (media_urls.length === 1) {
                // 1张图：全宽
                colSpan = 24;
                maxHeight = "400px";
              } else if (media_urls.length === 2) {
                // 2张图：各占一半
                colSpan = 12;
                maxHeight = "300px";
              } else if (media_urls.length === 3) {
                // 3张图：第一张全宽，后两张各占一半
                colSpan = index === 0 ? 24 : 12;
                maxHeight = index === 0 ? "300px" : "200px";
              } else {
                // 4张图：2x2网格
                colSpan = 12;
                maxHeight = "200px";
              }

              return (
                <Col span={colSpan} key={index}>
                  <Image
                    src={url}
                    alt={`Media ${index + 1}`}
                    style={{
                      borderRadius: "12px",
                      width: "100%",
                      height: maxHeight,
                      objectFit: "cover",
                      display: "block",
                    }}
                    preview={{
                      mask: "查看大图",
                    }}
                  />
                </Col>
              );
            })}
          </Row>
        </div>
      )}

      {/* 互动按钮 */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          paddingTop: "8px",
        }}
      >
        <Space size="large">
          {/* 回复 */}
          <Space size={4} style={{ cursor: "pointer" }}>
            <MessageOutlined style={{ fontSize: "18px", color: "#536471" }} />
            <Text type="secondary" style={{ fontSize: "13px" }}>
              {reply_count > 0 ? formatCount(reply_count) : ""}
            </Text>
          </Space>

          {/* 转发 */}
          <Space size={4} style={{ cursor: "pointer" }}>
            <RetweetOutlined style={{ fontSize: "18px", color: "#536471" }} />
            <Text type="secondary" style={{ fontSize: "13px" }}>
              {retweet_count > 0 ? formatCount(retweet_count) : ""}
            </Text>
          </Space>

          {/* 点赞 */}
          <Space
            size={4}
            style={{ cursor: "pointer" }}
            onClick={() => onLike && onLike(tweet_id)}
          >
            <HeartOutlined style={{ fontSize: "18px", color: "#536471" }} />
            <Text type="secondary" style={{ fontSize: "13px" }}>
              {like_count > 0 ? formatCount(like_count) : ""}
            </Text>
          </Space>

          {/* 查看原推 */}
          <Space
            size={4}
            style={{ cursor: "pointer" }}
            onClick={() => window.open(tweet_url, "_blank")}
          >
            <LinkOutlined style={{ fontSize: "18px", color: "#536471" }} />
          </Space>
        </Space>

        {/* 删除按钮 */}
        <Popconfirm
          title="确认删除"
          description="确定要删除这条推文吗？"
          onConfirm={handleDelete}
          okText="删除"
          cancelText="取消"
          okButtonProps={{ danger: true }}
        >
          <Button type="text" danger icon={<DeleteOutlined />} size="small">
            删除
          </Button>
        </Popconfirm>
      </div>
    </Card>
  );
};

export default TweetCard;
