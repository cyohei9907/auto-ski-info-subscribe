import React, { useState } from "react";
import {
  Card,
  Button,
  Table,
  Space,
  Modal,
  Form,
  Input,
  message,
  Popconfirm,
  Tag,
  Avatar,
  Typography,
  Select,
  Statistic,
  Row,
  Col,
  Dropdown,
  Menu,
} from "antd";
import {
  PlusOutlined,
  TwitterOutlined,
  EyeOutlined,
  DeleteOutlined,
  ReloadOutlined,
  SettingOutlined,
  FilterOutlined,
  DownOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "react-query";
import { monitorAPI } from "../services/api";

const { Title } = Typography;

const AccountsPage = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [form] = Form.useForm();
  const queryClient = useQueryClient();
  const [loadingAccountId, setLoadingAccountId] = useState(null);
  const [monitoringAccountId, setMonitoringAccountId] = useState(null);
  const [togglingAccountId, setTogglingAccountId] = useState(null);
  const [selectedRowKeys, setSelectedRowKeys] = useState([]); // 选中的行
  const [filterInterval, setFilterInterval] = useState(null); // 筛选的监控间隔

  const { data: accounts, isLoading } = useQuery(
    "accounts",
    monitorAPI.getAccounts
  );

  // デバッグログ
  console.log("=== AccountsPage Debug ===");
  console.log("Accounts data:", accounts);
  console.log("=========================");

  const addAccountMutation = useMutation(monitorAPI.addAccount, {
    onSuccess: () => {
      message.success("アカウントを追加しました");
      setIsModalVisible(false);
      form.resetFields();
      queryClient.invalidateQueries("accounts");
    },
    onError: (error) => {
      message.error(
        error.response?.data?.error || "アカウントの追加に失敗しました"
      );
    },
  });

  const deleteAccountMutation = useMutation(monitorAPI.deleteAccount, {
    onSuccess: () => {
      message.success("アカウントを削除しました");
      queryClient.invalidateQueries("accounts");
    },
    onError: () => {
      message.error("アカウントの削除に失敗しました");
    },
  });

  const updateAccountMutation = useMutation(
    ({ id, data }) => monitorAPI.updateAccount(id, data),
    {
      onMutate: ({ id, data }) => {
        // 如果是切换激活状态，显示loading
        if ("is_active" in data) {
          setTogglingAccountId(id);
        }
      },
      onSuccess: (response, { id, data }) => {
        // 根据更新的字段显示不同的消息
        if ("monitoring_interval" in data) {
          message.success("監視間隔を更新しました");
        } else if ("is_active" in data) {
          message.success("アカウントを更新しました");
        }

        // 更新特定账户的数据
        queryClient.setQueryData("accounts", (oldData) => {
          if (!oldData) return oldData;

          // 确保 oldData.data 是数组
          const currentAccounts = Array.isArray(oldData.data)
            ? oldData.data
            : [];

          if (currentAccounts.length === 0) return oldData;

          return {
            ...oldData,
            data: currentAccounts.map((account) =>
              account.id === id ? { ...account, ...data } : account
            ),
          };
        });

        setTogglingAccountId(null);
      },
      onError: () => {
        message.error("アカウントの更新に失敗しました");
        setTogglingAccountId(null);
      },
    }
  );

  const monitorNowMutation = useMutation(monitorAPI.monitorNow, {
    onMutate: (accountId) => {
      setMonitoringAccountId(accountId);
    },
    onSuccess: () => {
      message.success("監視タスクを開始しました");
      setMonitoringAccountId(null);
    },
    onError: () => {
      message.error("監視の開始に失敗しました");
      setMonitoringAccountId(null);
    },
  });

  const fetchLatestMutation = useMutation(monitorAPI.fetchLatestTweets, {
    onMutate: (accountId) => {
      console.log("fetchLatest onMutate - accountId:", accountId);
      setLoadingAccountId(accountId);
    },
    onSuccess: (response, accountId) => {
      console.log("fetchLatest onSuccess - response:", response);
      console.log("fetchLatest onSuccess - accountId:", accountId);

      const newTweets = response.data?.new_tweets || 0;
      message.success(`${newTweets}条の新しい推文を取得しました（24時間以内）`);

      queryClient.setQueryData("accounts", (oldData) => {
        console.log("fetchLatest - Old cache data:", oldData);
        console.log("fetchLatest - oldData.data type:", typeof oldData?.data);
        console.log(
          "fetchLatest - oldData.data is array:",
          Array.isArray(oldData?.data)
        );

        if (!oldData) return oldData;

        // 确保 oldData.data 是数组
        const currentAccounts = Array.isArray(oldData.data) ? oldData.data : [];

        if (currentAccounts.length === 0) {
          console.log("fetchLatest - No accounts in cache, returning oldData");
          return oldData;
        }

        const newData = {
          ...oldData,
          data: currentAccounts.map((account) =>
            account.id === accountId
              ? {
                  ...account,
                  tweets_count: (account.tweets_count || 0) + newTweets,
                }
              : account
          ),
        };

        console.log("fetchLatest - New cache data:", newData);
        return newData;
      });

      setLoadingAccountId(null);
    },
    onError: () => {
      message.error("推文の取得に失敗しました");
      setLoadingAccountId(null);
    },
  });

  const handleAddAccount = async (values) => {
    addAccountMutation.mutate(values.username);
  };

  const handleDeleteAccount = (id) => {
    deleteAccountMutation.mutate(id);
  };

  const handleToggleActive = (account) => {
    updateAccountMutation.mutate({
      id: account.id,
      data: { is_active: !account.is_active },
    });
  };

  const handleMonitorNow = (id) => {
    monitorNowMutation.mutate(id);
  };

  const handleFetchLatest = (id) => {
    fetchLatestMutation.mutate(id);
  };

  const columns = [
    {
      title: "アバター",
      dataIndex: "avatar_url",
      width: 60,
      fixed: "left",
      render: (avatar_url, record) =>
        avatar_url ? (
          <Avatar src={avatar_url} size={32} />
        ) : (
          <Avatar icon={<TwitterOutlined />} size={32} />
        ),
    },
    {
      title: "ユーザー名",
      dataIndex: "username",
      width: 150,
      render: (username) => `@${username}`,
    },
    {
      title: "表示名",
      dataIndex: "display_name",
      width: 150,
    },
    {
      title: "ツイート数",
      dataIndex: "tweets_count",
      width: 100,
      render: (count) => count || 0,
    },
    {
      title: "監視間隔",
      dataIndex: "monitoring_interval_display",
      width: 120,
      render: (display, record) => (
        <Select
          size="small"
          value={record.monitoring_interval}
          style={{ width: 110 }}
          onChange={(value) => {
            updateAccountMutation.mutate({
              id: record.id,
              data: { monitoring_interval: value },
            });
          }}
          options={[
            { value: 30, label: "30分ごと" },
            { value: 60, label: "1時間ごと" },
            { value: 240, label: "4時間ごと" },
            { value: 720, label: "12時間ごと" },
          ]}
        />
      ),
    },
    {
      title: "ステータス",
      dataIndex: "is_active",
      width: 120,
      render: (is_active, record) => (
        <Space direction="vertical" size={0}>
          <Tag color={is_active ? "green" : "red"}>
            {is_active ? "監視中" : "停止中"}
          </Tag>
          {record.last_checked && (
            <span style={{ fontSize: "11px", color: "#999" }}>
              最終:{" "}
              {new Date(record.last_checked).toLocaleTimeString("ja-JP", {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </span>
          )}
        </Space>
      ),
    },
    {
      title: "最終チェック",
      dataIndex: "last_checked",
      width: 150,
      render: (last_checked) =>
        last_checked
          ? new Date(last_checked).toLocaleString("ja-JP", {
              month: "2-digit",
              day: "2-digit",
              hour: "2-digit",
              minute: "2-digit",
            })
          : "未実行",
    },
    {
      title: "操作",
      key: "actions",
      width: 280,
      fixed: "right",
      render: (_, record) => (
        <Space size="small" wrap>
          <Button
            size="small"
            type={record.is_active ? "default" : "primary"}
            onClick={() => handleToggleActive(record)}
            loading={togglingAccountId === record.id}
          >
            {record.is_active ? "停止" : "開始"}
          </Button>
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleMonitorNow(record.id)}
            loading={monitoringAccountId === record.id}
            disabled={!record.is_active}
            title="今すぐ監視"
          />
          <Button
            size="small"
            icon={<ReloadOutlined />}
            onClick={() => handleFetchLatest(record.id)}
            loading={loadingAccountId === record.id}
            type="primary"
            title="24時間以内の全ての推文を取得"
          >
            当日全て
          </Button>
          <Popconfirm
            title="このアカウントを削除しますか？"
            onConfirm={() => handleDeleteAccount(record.id)}
            okText="削除"
            cancelText="キャンセル"
          >
            <Button
              size="small"
              type="text"
              danger
              icon={<DeleteOutlined />}
              loading={deleteAccountMutation.isLoading}
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 计算统计信息
  const accountsData = accounts?.data?.results || [];
  const intervalStats = {
    30: accountsData.filter((a) => a.monitoring_interval === 30).length,
    60: accountsData.filter((a) => a.monitoring_interval === 60).length,
    240: accountsData.filter((a) => a.monitoring_interval === 240).length,
    720: accountsData.filter((a) => a.monitoring_interval === 720).length,
  };

  // 应用筛选
  const filteredAccounts = filterInterval
    ? accountsData.filter((a) => a.monitoring_interval === filterInterval)
    : accountsData;

  // 批量设置监控间隔
  const handleBatchSetInterval = (interval) => {
    if (selectedRowKeys.length === 0) {
      message.warning("アカウントを選択してください");
      return;
    }

    Modal.confirm({
      title: "監視間隔を一括設定",
      content: `選択された${selectedRowKeys.length}件のアカウントの監視間隔を変更しますか？`,
      okText: "変更",
      cancelText: "キャンセル",
      onOk: async () => {
        try {
          await Promise.all(
            selectedRowKeys.map((id) =>
              monitorAPI.updateAccount(id, { monitoring_interval: interval })
            )
          );
          message.success("監視間隔を一括更新しました");
          queryClient.invalidateQueries("accounts");
          setSelectedRowKeys([]);
        } catch (error) {
          message.error("一括更新に失敗しました");
        }
      },
    });
  };

  // 批量操作菜单
  const batchMenu = (
    <Menu>
      <Menu.Item key="30" onClick={() => handleBatchSetInterval(30)}>
        30分ごとに設定
      </Menu.Item>
      <Menu.Item key="60" onClick={() => handleBatchSetInterval(60)}>
        1時間ごとに設定
      </Menu.Item>
      <Menu.Item key="240" onClick={() => handleBatchSetInterval(240)}>
        4時間ごとに設定
      </Menu.Item>
      <Menu.Item key="720" onClick={() => handleBatchSetInterval(720)}>
        12時間ごとに設定
      </Menu.Item>
    </Menu>
  );

  // 表格行选择配置
  const rowSelection = {
    selectedRowKeys,
    onChange: setSelectedRowKeys,
  };

  return (
    <div>
      <div className="page-header">
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <Title level={2} style={{ margin: 0 }}>
              アカウント管理
            </Title>
            <p style={{ margin: "8px 0 0 0", color: "#666" }}>
              監視するX (Twitter) アカウントを管理します
            </p>
          </div>
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={() => queryClient.invalidateQueries("accounts")}
              loading={isLoading}
            >
              更新
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setIsModalVisible(true)}
            >
              アカウント追加
            </Button>
          </Space>
        </div>
      </div>

      {/* 统计信息卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="総アカウント数"
              value={accountsData.length}
              prefix={<TwitterOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card
            hoverable
            onClick={() => setFilterInterval(filterInterval === 30 ? null : 30)}
            style={{
              borderColor: filterInterval === 30 ? "#1890ff" : undefined,
            }}
          >
            <Statistic
              title="30分間隔"
              value={intervalStats[30]}
              valueStyle={{
                color: filterInterval === 30 ? "#1890ff" : undefined,
              }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card
            hoverable
            onClick={() => setFilterInterval(filterInterval === 60 ? null : 60)}
            style={{
              borderColor: filterInterval === 60 ? "#1890ff" : undefined,
            }}
          >
            <Statistic
              title="1時間間隔"
              value={intervalStats[60]}
              valueStyle={{
                color: filterInterval === 60 ? "#1890ff" : undefined,
              }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card
            hoverable
            onClick={() =>
              setFilterInterval(filterInterval === 240 ? null : 240)
            }
            style={{
              borderColor: filterInterval === 240 ? "#1890ff" : undefined,
            }}
          >
            <Statistic
              title="4時間間隔"
              value={intervalStats[240]}
              valueStyle={{
                color: filterInterval === 240 ? "#1890ff" : undefined,
              }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card
            hoverable
            onClick={() =>
              setFilterInterval(filterInterval === 720 ? null : 720)
            }
            style={{
              borderColor: filterInterval === 720 ? "#1890ff" : undefined,
            }}
          >
            <Statistic
              title="12時間間隔"
              value={intervalStats[720]}
              valueStyle={{
                color: filterInterval === 720 ? "#1890ff" : undefined,
              }}
            />
          </Card>
        </Col>
        <Col span={18}>
          <Card>
            <Space>
              <Dropdown
                overlay={batchMenu}
                disabled={selectedRowKeys.length === 0}
              >
                <Button icon={<SettingOutlined />}>
                  一括設定 ({selectedRowKeys.length}) <DownOutlined />
                </Button>
              </Dropdown>
              {filterInterval && (
                <Tag
                  closable
                  onClose={() => setFilterInterval(null)}
                  color="blue"
                >
                  <FilterOutlined /> フィルター:{" "}
                  {filterInterval === 30
                    ? "30分"
                    : filterInterval === 60
                    ? "1時間"
                    : filterInterval === 240
                    ? "4時間"
                    : "12時間"}
                </Tag>
              )}
            </Space>
          </Card>
        </Col>
      </Row>

      <Card>
        <Table
          columns={columns}
          dataSource={filteredAccounts}
          loading={isLoading}
          rowKey="id"
          rowSelection={rowSelection}
          scroll={{ x: 800 }}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} / ${total} 件`,
            responsive: true,
          }}
        />
      </Card>

      <Modal
        title="新しいアカウントを追加"
        open={isModalVisible}
        onCancel={() => {
          setIsModalVisible(false);
          form.resetFields();
        }}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleAddAccount}>
          <Form.Item
            name="username"
            label="X (Twitter) ユーザー名"
            rules={[
              { required: true, message: "ユーザー名を入力してください" },
              {
                pattern: /^[a-zA-Z0-9_]+$/,
                message: "有効なユーザー名を入力してください",
              },
            ]}
          >
            <Input prefix="@" placeholder="username" maxLength={15} />
          </Form.Item>
          <Form.Item>
            <Space style={{ width: "100%", justifyContent: "flex-end" }}>
              <Button onClick={() => setIsModalVisible(false)}>
                キャンセル
              </Button>
              <Button
                type="primary"
                htmlType="submit"
                loading={addAccountMutation.isLoading}
              >
                追加
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default AccountsPage;
