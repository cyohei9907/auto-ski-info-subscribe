import React, { useState, useEffect } from "react";
import {
  Card,
  Button,
  List,
  Space,
  Typography,
  Select,
  DatePicker,
  Switch,
  Row,
  Col,
  Statistic,
  message,
  Empty,
  Spin,
  Popconfirm,
} from "antd";
import {
  SyncOutlined,
  FilterOutlined,
  CalendarOutlined,
  DeleteOutlined,
} from "@ant-design/icons";
import { monitorAPI } from "../services/api";
import TweetCard from "../components/TweetCard";
import dayjs from "dayjs";

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

const TweetsPage = () => {
  const [accounts, setAccounts] = useState([]);
  const [tweets, setTweets] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [aiFilterEnabled, setAiFilterEnabled] = useState(false);
  const [dateRange, setDateRange] = useState(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState({ total: 0, today: 0, aiRecommended: 0 });

  // Debug: Log accounts state
  console.log(
    "TweetsPage render - accounts:",
    accounts,
    "isArray:",
    Array.isArray(accounts)
  );

  // Safety check: ensure accounts is always an array
  useEffect(() => {
    if (!Array.isArray(accounts)) {
      console.error("CRITICAL: accounts is not an array!", accounts);
      setAccounts([]);
    }
  }, [accounts]);

  // 加载账户列表
  useEffect(() => {
    loadAccounts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 加载推文
  useEffect(() => {
    if (selectedAccount) {
      loadTweets();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedAccount, aiFilterEnabled, dateRange]);

  const loadAccounts = async () => {
    try {
      const response = await monitorAPI.getAccounts();
      console.log("API response:", response.data);

      // Handle both paginated and non-paginated responses
      let accountsData = [];
      if (response.data) {
        if (Array.isArray(response.data)) {
          // Direct array response
          accountsData = response.data;
        } else if (
          response.data.results &&
          Array.isArray(response.data.results)
        ) {
          // Paginated response with results field
          accountsData = response.data.results;
        }
      }

      console.log("Parsed accounts:", accountsData);
      setAccounts(accountsData);

      if (accountsData.length > 0 && !selectedAccount) {
        const firstAccount = accountsData[0];
        setSelectedAccount(firstAccount.id);
        setAiFilterEnabled(firstAccount.ai_filter_enabled || false);
        if (firstAccount.fetch_from_date && firstAccount.fetch_to_date) {
          setDateRange([
            dayjs(firstAccount.fetch_from_date),
            dayjs(firstAccount.fetch_to_date),
          ]);
        }
      }
    } catch (error) {
      console.error("Failed to load accounts:", error);
      message.error("加载账户列表失败");
      setAccounts([]);
    }
  };

  const loadTweets = async () => {
    setLoading(true);
    try {
      const params = {
        account_id: selectedAccount,
      };

      if (aiFilterEnabled) {
        params.ai_filter = true;
      }

      if (dateRange && dateRange[0] && dateRange[1]) {
        params.from_date = dateRange[0].format("YYYY-MM-DD");
        params.to_date = dateRange[1].format("YYYY-MM-DD");
      }

      const response = await monitorAPI.getTweets(params);
      const tweetsData = Array.isArray(response.data?.results)
        ? response.data.results
        : Array.isArray(response.data)
        ? response.data
        : [];
      setTweets(tweetsData);

      // 计算统计信息
      const today = dayjs().format("YYYY-MM-DD");
      const todayTweets = tweetsData.filter(
        (t) => dayjs(t.posted_at).format("YYYY-MM-DD") === today
      );
      const aiRecommended = tweetsData.filter((t) => t.ai_relevant);

      setStats({
        total: tweetsData.length,
        today: todayTweets.length,
        aiRecommended: aiRecommended.length,
      });
    } catch (error) {
      console.error("Failed to load tweets:", error);
      message.error("加载推文失败");
      setTweets([]);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    if (!selectedAccount) return;

    setRefreshing(true);
    try {
      await monitorAPI.fetchLatestTweets(selectedAccount); // 修正：使用正确的API方法
      message.success("刷新成功,正在获取最新推文...");
      setTimeout(() => loadTweets(), 2000);
    } catch (error) {
      console.error("Refresh error:", error);
      message.error(
        "刷新失败: " + (error.response?.data?.error || error.message)
      );
    } finally {
      setRefreshing(false);
    }
  };

  const handleAccountChange = (accountId) => {
    setSelectedAccount(accountId);
    if (!Array.isArray(accounts)) return;

    const account = accounts.find((a) => a.id === accountId);
    if (account) {
      setAiFilterEnabled(account.ai_filter_enabled || false);
      if (account.fetch_from_date && account.fetch_to_date) {
        setDateRange([
          dayjs(account.fetch_from_date),
          dayjs(account.fetch_to_date),
        ]);
      } else {
        setDateRange(null);
      }
    }
  };

  const handleAiFilterToggle = async (checked) => {
    if (!selectedAccount) return;

    try {
      await monitorAPI.updateAccount(selectedAccount, {
        ai_filter_enabled: checked,
      });
      setAiFilterEnabled(checked);
      message.success(checked ? "已开启智能推荐" : "已关闭智能推荐");
    } catch (error) {
      message.error("更新设置失败");
    }
  };

  const handleDateRangeChange = async (dates) => {
    if (!selectedAccount) return;

    if (!dates) {
      try {
        await monitorAPI.updateAccount(selectedAccount, {
          fetch_from_date: null,
          fetch_to_date: null,
        });
        setDateRange(null);
        message.success("已清除日期范围限制");
      } catch (error) {
        message.error("更新日期范围失败");
      }
      return;
    }

    try {
      await monitorAPI.updateAccount(selectedAccount, {
        fetch_from_date: dates[0].format("YYYY-MM-DD"),
        fetch_to_date: dates[1].format("YYYY-MM-DD"),
      });
      setDateRange(dates);
      message.success("日期范围已更新");
    } catch (error) {
      message.error("更新日期范围失败");
    }
  };

  const handleDeleteTweet = (tweetId) => {
    // 从列表中移除已删除的推文
    setTweets(tweets.filter((t) => t.id !== tweetId));
    // 重新加载统计信息
    loadTweets();
  };

  const handleDeleteAllTweets = async () => {
    if (!selectedAccount) return;

    try {
      const response = await monitorAPI.deleteAccountTweets(selectedAccount);
      message.success(`已删除 ${response.data.deleted_count} 条推文`);
      setTweets([]);
      loadTweets();
    } catch (error) {
      message.error(
        "批量删除失败: " + (error.response?.data?.message || error.message)
      );
    }
  };

  const selectedAccountData = Array.isArray(accounts)
    ? accounts.find((a) => a.id === selectedAccount)
    : null;

  return (
    <div style={{ padding: "24px" }}>
      {/* 页头 */}
      <div style={{ marginBottom: "24px" }}>
        <Title level={2}>推文监控</Title>
        <Text type="secondary">查看和管理监控的 X (Twitter) 账户推文</Text>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: "24px" }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="总推文数"
              value={stats.total}
              prefix={<SyncOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="今日推文"
              value={stats.today}
              prefix={<CalendarOutlined />}
              valueStyle={{ color: "#3f8600" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="AI 推荐"
              value={stats.aiRecommended}
              prefix="⭐"
              valueStyle={{ color: "#cf1322" }}
            />
          </Card>
        </Col>
      </Row>

      {/* 控制面板 */}
      <Card style={{ marginBottom: "24px" }}>
        <Space direction="vertical" size="middle" style={{ width: "100%" }}>
          {/* 账户选择 */}
          <div>
            <Text strong>选择账户: </Text>
            <Select
              style={{ width: "300px", marginLeft: "8px" }}
              value={selectedAccount}
              onChange={handleAccountChange}
              placeholder="选择要查看的账户"
            >
              {Array.isArray(accounts) &&
                accounts.map((account) => (
                  <Option key={account.id} value={account.id}>
                    <Space>
                      @{account.username}
                      {account.display_name && `(${account.display_name})`}
                    </Space>
                  </Option>
                ))}
            </Select>
          </div>

          {/* 控制选项 */}
          <Space wrap>
            {/* 智能推荐开关 */}
            <Space>
              <FilterOutlined />
              <Text>智能推荐:</Text>
              <Switch
                checked={aiFilterEnabled}
                onChange={handleAiFilterToggle}
                checkedChildren="开启"
                unCheckedChildren="关闭"
              />
            </Space>

            {/* 日期范围选择 */}
            <Space>
              <CalendarOutlined />
              <Text>日期范围:</Text>
              <RangePicker
                value={dateRange}
                onChange={handleDateRangeChange}
                format="YYYY-MM-DD"
                placeholder={["开始日期", "结束日期"]}
              />
            </Space>

            {/* 刷新按钮 */}
            <Button
              type="primary"
              icon={<SyncOutlined spin={refreshing} />}
              onClick={handleRefresh}
              loading={refreshing}
            >
              刷新推文
            </Button>

            {/* 批量删除按钮 */}
            {selectedAccount && tweets.length > 0 && (
              <Popconfirm
                title="批量删除推文"
                description={`确定要删除 @${selectedAccountData?.username} 的所有 ${tweets.length} 条推文吗？此操作不可恢复！`}
                onConfirm={handleDeleteAllTweets}
                okText="确认删除"
                cancelText="取消"
                okButtonProps={{ danger: true }}
              >
                <Button danger icon={<DeleteOutlined />}>
                  删除所有推文
                </Button>
              </Popconfirm>
            )}
          </Space>
        </Space>
      </Card>

      {/* 推文列表 */}
      <Card
        title={
          <Space>
            <Text strong>推文时间线</Text>
            {selectedAccountData && (
              <Text type="secondary">@{selectedAccountData.username}</Text>
            )}
          </Space>
        }
        styles={{ body: { padding: "16px" } }}
      >
        {loading ? (
          <div style={{ textAlign: "center", padding: "40px" }}>
            <Spin size="large" />
          </div>
        ) : tweets.length === 0 ? (
          <Empty
            description={
              <span>
                {selectedAccount
                  ? "暂无推文数据,请点击刷新按钮获取最新推文"
                  : "请选择要查看的账户"}
              </span>
            }
          />
        ) : (
          <List
            dataSource={tweets}
            renderItem={(tweet) => (
              <TweetCard
                key={tweet.id}
                tweet={tweet}
                onDelete={handleDeleteTweet}
              />
            )}
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 条推文`,
            }}
          />
        )}
      </Card>
    </div>
  );
};

export default TweetsPage;
