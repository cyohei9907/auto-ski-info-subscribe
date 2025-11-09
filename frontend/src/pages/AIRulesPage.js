import React, { useState } from "react";
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  Switch,
  Select,
  message,
  Popconfirm,
  Tooltip,
  Typography,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "react-query";
import { aiAPI, monitorAPI } from "../services/api";

const { TextArea } = Input;
const { Option } = Select;
const { Text } = Typography;

function AIRulesPage() {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingRule, setEditingRule] = useState(null);
  const [applyingRule, setApplyingRule] = useState(null);
  const [form] = Form.useForm();
  const queryClient = useQueryClient();

  // 获取规则列表
  const { data: rulesData, isLoading } = useQuery(
    "aiRules",
    () => aiAPI.getRules().then((res) => res.data),
    {
      refetchInterval: 30000, // 30秒自动刷新
    }
  );

  // 获取账号列表
  const { data: accountsData } = useQuery("accounts", () =>
    monitorAPI.getAccounts().then((res) => res.data)
  );

  // 确保rulesData是数组
  const rules = Array.isArray(rulesData) ? rulesData : [];
  const accounts = Array.isArray(accountsData) ? accountsData : [];

  // 创建/更新规则
  const saveMutation = useMutation(
    (data) => {
      if (editingRule) {
        return aiAPI.updateRule(editingRule.id, data);
      }
      return aiAPI.createRule(data);
    },
    {
      onSuccess: () => {
        message.success(editingRule ? "规则已更新" : "规则已创建");
        setIsModalVisible(false);
        setEditingRule(null);
        form.resetFields();
        queryClient.invalidateQueries("aiRules");
      },
      onError: (error) => {
        message.error(
          `操作失败: ${error.response?.data?.detail || error.message}`
        );
      },
    }
  );

  // 删除规则
  const deleteMutation = useMutation((id) => aiAPI.deleteRule(id), {
    onSuccess: () => {
      message.success("规则已删除");
      queryClient.invalidateQueries("aiRules");
    },
    onError: (error) => {
      message.error(
        `删除失败: ${error.response?.data?.detail || error.message}`
      );
    },
  });

  // 应用规则
  const applyMutation = useMutation(
    ({ ruleId, dateFilter }) => aiAPI.applyRule(ruleId, dateFilter),
    {
      onSuccess: (response) => {
        const count = response.data.recommended_count;
        message.success(`规则应用成功！筛选出 ${count} 条推文`);
        setApplyingRule(null);
        queryClient.invalidateQueries("aiRules");
        queryClient.invalidateQueries("recommendedTweets");
      },
      onError: (error) => {
        message.error(
          `应用失败: ${error.response?.data?.detail || error.message}`
        );
        setApplyingRule(null);
      },
    }
  );

  const handleCreate = () => {
    setEditingRule(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingRule(record);
    // 设置表单值，包括target_accounts的ID数组
    form.setFieldsValue({
      ...record,
      target_accounts: record.target_accounts || [],
    });
    setIsModalVisible(true);
  };

  const handleDelete = (id) => {
    deleteMutation.mutate(id);
  };

  const handleApply = (rule, dateFilter) => {
    setApplyingRule(rule.id);
    applyMutation.mutate({ ruleId: rule.id, dateFilter });
  };

  const handleModalOk = () => {
    form.validateFields().then((values) => {
      saveMutation.mutate(values);
    });
  };

  const handleModalCancel = () => {
    setIsModalVisible(false);
    setEditingRule(null);
    form.resetFields();
  };

  const columns = [
    {
      title: "规则名称",
      dataIndex: "name",
      key: "name",
      width: 180,
      ellipsis: true,
    },
    {
      title: "筛选提示词",
      dataIndex: "prompt",
      key: "prompt",
      ellipsis: true,
      render: (text) => (
        <Tooltip title={text}>
          <Text ellipsis style={{ maxWidth: 300 }}>
            {text}
          </Text>
        </Tooltip>
      ),
    },
    {
      title: "应用账号",
      dataIndex: "target_account_details",
      key: "target_accounts",
      width: 200,
      render: (accounts) => {
        if (!accounts || accounts.length === 0) {
          return <Tag color="blue">全部账号</Tag>;
        }
        return (
          <Space wrap>
            {accounts.slice(0, 3).map((account) => (
              <Tooltip
                key={account.id}
                title={account.display_name || account.username}
              >
                <Tag color="purple">@{account.username}</Tag>
              </Tooltip>
            ))}
            {accounts.length > 3 && <Tag>+{accounts.length - 3}</Tag>}
          </Space>
        );
      },
    },
    {
      title: "状态",
      dataIndex: "is_active",
      key: "is_active",
      width: 80,
      align: "center",
      render: (isActive) => (
        <Tag color={isActive ? "success" : "default"}>
          {isActive ? "启用" : "禁用"}
        </Tag>
      ),
    },
    {
      title: "推荐数量",
      dataIndex: "recommended_count",
      key: "recommended_count",
      width: 100,
      align: "center",
      render: (count) => <Tag color="blue">{count}</Tag>,
    },
    {
      title: "上次应用",
      dataIndex: "last_applied",
      key: "last_applied",
      width: 180,
      render: (date) =>
        date ? new Date(date).toLocaleString("zh-CN") : "从未应用",
    },
    {
      title: "创建时间",
      dataIndex: "created_at",
      key: "created_at",
      width: 180,
      render: (date) => new Date(date).toLocaleString("zh-CN"),
    },
    {
      title: "操作",
      key: "actions",
      width: 200,
      fixed: "right",
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="应用规则">
            <Button
              type="primary"
              size="small"
              icon={<PlayCircleOutlined />}
              loading={applyingRule === record.id}
              onClick={() => {
                Modal.confirm({
                  title: "应用AI筛选规则",
                  content: (
                    <div>
                      <p>选择要筛选的推文时间范围：</p>
                      <Select
                        id="date-filter-select"
                        defaultValue="today"
                        style={{ width: "100%" }}
                      >
                        <Option value="today">今天</Option>
                        <Option value="week">最近一周</Option>
                        <Option value="all">全部</Option>
                      </Select>
                    </div>
                  ),
                  onOk: () => {
                    const dateFilter =
                      document.getElementById("date-filter-select")?.value ||
                      "today";
                    handleApply(record, dateFilter);
                  },
                });
              }}
            >
              应用
            </Button>
          </Tooltip>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除此规则？"
            description="删除后无法恢复，相关的推荐记录也会被删除。"
            onConfirm={() => handleDelete(record.id)}
            okText="删除"
            cancelText="取消"
            okButtonProps={{ danger: true }}
          >
            <Button size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: "24px" }}>
      <Card
        title="AI推荐规则管理"
        extra={
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={() => queryClient.invalidateQueries("aiRules")}
            >
              刷新
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleCreate}
            >
              新建规则
            </Button>
          </Space>
        }
      >
        <Table
          dataSource={rules}
          columns={columns}
          rowKey="id"
          loading={isLoading}
          scroll={{ x: 1200 }}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条规则`,
          }}
        />
      </Card>

      <Modal
        title={editingRule ? "编辑规则" : "新建规则"}
        open={isModalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        width={700}
        confirmLoading={saveMutation.isLoading}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="规则名称"
            name="name"
            rules={[
              { required: true, message: "请输入规则名称" },
              { max: 255, message: "名称不能超过255个字符" },
            ]}
          >
            <Input placeholder="例如：白马47滑雪场推文筛选" />
          </Form.Item>

          <Form.Item
            label="筛选提示词"
            name="prompt"
            rules={[{ required: true, message: "请输入AI筛选提示词" }]}
            tooltip="描述你想要筛选的推文内容，AI会根据这个提示词来判断推文是否相关"
          >
            <TextArea
              rows={6}
              placeholder={`例如：请筛选出所有与"白马47滑雪场"相关的推文，包括：
- 直接提到白马47、Hakuba 47的推文
- 讨论白马47雪况、设施的推文
- 分享白马47滑雪体验的推文
- 白马47活动、优惠信息的推文`}
            />
          </Form.Item>

          <Form.Item
            label="应用账号"
            name="target_accounts"
            tooltip="选择要应用此规则的Twitter账号。不选择表示应用到所有监控的账号。"
          >
            <Select
              mode="multiple"
              placeholder="留空表示应用到所有账号"
              allowClear
              showSearch
              filterOption={(input, option) =>
                option.children.toLowerCase().includes(input.toLowerCase())
              }
            >
              {accounts.map((account) => (
                <Option key={account.id} value={account.id}>
                  @{account.username}{" "}
                  {account.display_name && `(${account.display_name})`}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="启用状态"
            name="is_active"
            valuePropName="checked"
            initialValue={true}
          >
            <Switch checkedChildren="启用" unCheckedChildren="禁用" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default AIRulesPage;
