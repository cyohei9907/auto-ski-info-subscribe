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
} from "antd";
import {
  PlusOutlined,
  TwitterOutlined,
  EyeOutlined,
  DeleteOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "react-query";
import { monitorAPI } from "../services/api";

const { Title } = Typography;

const AccountsPage = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [form] = Form.useForm();
  const queryClient = useQueryClient();

  const { data: accounts, isLoading } = useQuery(
    "accounts",
    monitorAPI.getAccounts
  );

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
      onSuccess: () => {
        message.success("アカウントを更新しました");
        queryClient.invalidateQueries("accounts");
      },
      onError: () => {
        message.error("アカウントの更新に失敗しました");
      },
    }
  );

  const monitorNowMutation = useMutation(monitorAPI.monitorNow, {
    onSuccess: () => {
      message.success("監視タスクを開始しました");
    },
    onError: () => {
      message.error("監視の開始に失敗しました");
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
      title: "ステータス",
      dataIndex: "is_active",
      width: 100,
      render: (is_active) => (
        <Tag color={is_active ? "green" : "red"}>
          {is_active ? "監視中" : "停止中"}
        </Tag>
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
      width: 200,
      fixed: "right",
      render: (_, record) => (
        <Space size="small">
          <Button
            size="small"
            type={record.is_active ? "default" : "primary"}
            onClick={() => handleToggleActive(record)}
            loading={updateAccountMutation.isLoading}
          >
            {record.is_active ? "停止" : "開始"}
          </Button>
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleMonitorNow(record.id)}
            loading={monitorNowMutation.isLoading}
            disabled={!record.is_active}
            title="今すぐ監視"
          />
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

      <Card>
        <Table
          columns={columns}
          dataSource={accounts?.data?.results || []}
          loading={isLoading}
          rowKey="id"
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
