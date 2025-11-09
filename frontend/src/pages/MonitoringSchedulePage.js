import React, { useState, useEffect } from "react";
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Button,
  message,
  Space,
  Tag,
  Progress,
  Tooltip,
} from "antd";
import {
  ClockCircleOutlined,
  ThunderboltOutlined,
  DollarOutlined,
  SyncOutlined,
  BulbOutlined,
} from "@ant-design/icons";
import api from "../services/api";

export default function MonitoringSchedulePage() {
  const [loading, setLoading] = useState(false);
  const [scheduleStats, setScheduleStats] = useState(null);
  const [recommendations, setRecommendations] = useState([]);

  // 获取调度统计
  const fetchScheduleStats = async () => {
    try {
      setLoading(true);
      const response = await api.get("/monitor/monitoring-schedule/");
      setScheduleStats(response.data);
    } catch (error) {
      message.error(
        "获取调度统计失败: " + (error.response?.data?.error || error.message)
      );
    } finally {
      setLoading(false);
    }
  };

  // 获取优化建议
  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      const response = await api.get("/monitor/optimize-intervals/");
      setRecommendations(response.data.recommendations || []);
      if (response.data.recommendations?.length === 0) {
        message.success("当前所有账号的监控间隔都已优化！");
      }
    } catch (error) {
      message.error(
        "获取优化建议失败: " + (error.response?.data?.error || error.message)
      );
    } finally {
      setLoading(false);
    }
  };

  // 应用优化建议
  const applyRecommendation = async (accountId, recommendedInterval) => {
    try {
      await api.patch(`/monitor/accounts/${accountId}/`, {
        monitoring_interval: recommendedInterval,
      });
      message.success("已应用优化建议");
      fetchScheduleStats();
      fetchRecommendations();
    } catch (error) {
      message.error(
        "应用失败: " + (error.response?.data?.error || error.message)
      );
    }
  };

  useEffect(() => {
    fetchScheduleStats();
    fetchRecommendations();
  }, []);

  // 间隔标签颜色映射
  const intervalColors = {
    30: "red",
    60: "orange",
    240: "blue",
    720: "green",
  };

  // 间隔描述
  const intervalLabels = {
    30: "30分钟（高频）",
    60: "1小时（中频）",
    240: "4小时（低频）",
    720: "12小时（极低频）",
  };

  // 统计卡片数据
  const statsData = scheduleStats
    ? [
        {
          title: "总账号数",
          value: scheduleStats.total_accounts,
          icon: <ClockCircleOutlined />,
          color: "#1890ff",
        },
        {
          title: "每日调用次数",
          value: scheduleStats.total_daily_calls,
          icon: <ThunderboltOutlined />,
          color: "#52c41a",
        },
        {
          title: "每月调用次数",
          value: scheduleStats.total_monthly_calls,
          icon: <SyncOutlined />,
          color: "#faad14",
        },
        {
          title: "预估月成本",
          value: `$${scheduleStats.estimated_monthly_cost_usd}`,
          icon: <DollarOutlined />,
          color: "#f5222d",
        },
      ]
    : [];

  // 分级统计表格
  const intervalStatsColumns = [
    {
      title: "监控间隔",
      dataIndex: "interval",
      key: "interval",
      render: (interval) => (
        <Tag color={intervalColors[interval]}>{intervalLabels[interval]}</Tag>
      ),
    },
    {
      title: "账号数量",
      dataIndex: "count",
      key: "count",
    },
    {
      title: "每日运行次数",
      dataIndex: "daily_runs",
      key: "daily_runs",
    },
    {
      title: "每日总调用",
      key: "total_calls",
      render: (_, record) => record.count * record.daily_runs,
    },
    {
      title: "占比",
      key: "percentage",
      render: (_, record) => {
        if (!scheduleStats) return "-";
        const percentage = (record.count / scheduleStats.total_accounts) * 100;
        return (
          <Progress
            percent={percentage}
            size="small"
            format={(percent) => `${percent.toFixed(1)}%`}
          />
        );
      },
    },
  ];

  const intervalStatsData = scheduleStats?.stats
    ? Object.keys(scheduleStats.stats).map((interval) => ({
        interval,
        count: scheduleStats.stats[interval].count,
        daily_runs: scheduleStats.stats[interval].daily_runs,
      }))
    : [];

  // 优化建议表格
  const recommendationColumns = [
    {
      title: "账号",
      dataIndex: "username",
      key: "username",
      render: (username) => `@${username}`,
    },
    {
      title: "当前间隔",
      dataIndex: "current_interval",
      key: "current_interval",
      render: (interval) => (
        <Tag color={intervalColors[interval]}>{intervalLabels[interval]}</Tag>
      ),
    },
    {
      title: "建议间隔",
      dataIndex: "recommended_interval",
      key: "recommended_interval",
      render: (interval) => (
        <Tag color={intervalColors[interval]}>{intervalLabels[interval]}</Tag>
      ),
    },
    {
      title: "平均每日推文数",
      dataIndex: "avg_daily_tweets",
      key: "avg_daily_tweets",
      render: (value) => value.toFixed(2),
    },
    {
      title: "理由",
      dataIndex: "reason",
      key: "reason",
    },
    {
      title: "预计节省",
      dataIndex: "potential_savings",
      key: "potential_savings",
      render: (value) => (
        <Tooltip title="降低监控频率可节省的成本比例">
          <Tag color="green">{value.toFixed(1)}%</Tag>
        </Tooltip>
      ),
    },
    {
      title: "操作",
      key: "action",
      render: (_, record) => (
        <Button
          type="primary"
          size="small"
          onClick={() =>
            applyRecommendation(record.account_id, record.recommended_interval)
          }
        >
          应用
        </Button>
      ),
    },
  ];

  return (
    <div style={{ padding: "24px" }}>
      <h2>
        <ClockCircleOutlined /> 智能监控调度管理
      </h2>
      <p style={{ marginBottom: "24px", color: "#666" }}>
        通过智能分级调度，根据账号活跃度优化监控频率，最高节省 50% 成本
      </p>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: "24px" }}>
        {statsData.map((stat, index) => (
          <Col span={6} key={index}>
            <Card>
              <Statistic
                title={stat.title}
                value={stat.value}
                prefix={stat.icon}
                valueStyle={{ color: stat.color }}
              />
            </Card>
          </Col>
        ))}
      </Row>

      {/* 成本明细 */}
      {scheduleStats && (
        <Card title="成本明细" style={{ marginBottom: "24px" }}>
          <Row gutter={16}>
            <Col span={12}>
              <Statistic
                title="CPU 成本"
                value={scheduleStats.cost_breakdown.cpu_cost_usd}
                prefix="$"
                precision={2}
              />
            </Col>
            <Col span={12}>
              <Statistic
                title="内存成本"
                value={scheduleStats.cost_breakdown.memory_cost_usd}
                prefix="$"
                precision={2}
              />
            </Col>
          </Row>
        </Card>
      )}

      {/* 分级统计 */}
      <Card
        title="监控间隔分布"
        style={{ marginBottom: "24px" }}
        extra={
          <Button
            icon={<SyncOutlined />}
            onClick={fetchScheduleStats}
            loading={loading}
          >
            刷新
          </Button>
        }
      >
        <Table
          columns={intervalStatsColumns}
          dataSource={intervalStatsData}
          rowKey="interval"
          pagination={false}
          loading={loading}
        />
      </Card>

      {/* 优化建议 */}
      <Card
        title={
          <Space>
            <BulbOutlined style={{ color: "#faad14" }} />
            智能优化建议
          </Space>
        }
        extra={
          <Button
            icon={<SyncOutlined />}
            onClick={fetchRecommendations}
            loading={loading}
          >
            重新分析
          </Button>
        }
      >
        {recommendations.length > 0 ? (
          <>
            <p style={{ marginBottom: "16px", color: "#666" }}>
              根据过去 7 天的推文数量，为您推荐更合适的监控间隔：
            </p>
            <Table
              columns={recommendationColumns}
              dataSource={recommendations}
              rowKey="account_id"
              pagination={false}
              loading={loading}
            />
          </>
        ) : (
          <p style={{ textAlign: "center", padding: "40px", color: "#999" }}>
            🎉 当前所有账号的监控间隔都已优化！
          </p>
        )}
      </Card>

      {/* 说明文档 */}
      <Card title="监控间隔说明" style={{ marginTop: "24px" }}>
        <Row gutter={16}>
          <Col span={6}>
            <Tag
              color="red"
              style={{ width: "100%", textAlign: "center", padding: "8px" }}
            >
              30分钟
            </Tag>
            <p style={{ marginTop: "8px", textAlign: "center" }}>
              高活跃账号
              <br />
              每天 &gt;10 条推文
              <br />
              每日调用 48 次
            </p>
          </Col>
          <Col span={6}>
            <Tag
              color="orange"
              style={{ width: "100%", textAlign: "center", padding: "8px" }}
            >
              1小时
            </Tag>
            <p style={{ marginTop: "8px", textAlign: "center" }}>
              中活跃账号
              <br />
              每天 5-10 条推文
              <br />
              每日调用 24 次
            </p>
          </Col>
          <Col span={6}>
            <Tag
              color="blue"
              style={{ width: "100%", textAlign: "center", padding: "8px" }}
            >
              4小时
            </Tag>
            <p style={{ marginTop: "8px", textAlign: "center" }}>
              低活跃账号
              <br />
              每天 1-5 条推文
              <br />
              每日调用 6 次
            </p>
          </Col>
          <Col span={6}>
            <Tag
              color="green"
              style={{ width: "100%", textAlign: "center", padding: "8px" }}
            >
              12小时
            </Tag>
            <p style={{ marginTop: "8px", textAlign: "center" }}>
              极低活跃账号
              <br />
              每天 &lt;1 条推文
              <br />
              每日调用 2 次
            </p>
          </Col>
        </Row>
      </Card>
    </div>
  );
}
