import React, { useState } from "react";
import {
  Card,
  Form,
  Input,
  Button,
  Switch,
  Alert,
  Tabs,
  Typography,
  message,
  Space,
} from "antd";
import {
  LockOutlined,
  UserOutlined,
  LoginOutlined,
  FileTextOutlined,
  CloudUploadOutlined,
} from "@ant-design/icons";
import { setupXAuthentication, uploadXCookies } from "../services/api";

const { Title, Text } = Typography;
const { TextArea } = Input;

function SettingsPage() {
  const [autoLoginForm] = Form.useForm();
  const [cookieForm] = Form.useForm();
  const [autoLoginLoading, setAutoLoginLoading] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [result, setResult] = useState(null);

  // 自动登录处理
  const handleAutoLogin = async (values) => {
    setAutoLoginLoading(true);
    setResult(null);

    try {
      const response = await setupXAuthentication({
        username: values.username,
        password: values.password,
        headless: values.headless !== false,
      });

      if (response.success) {
        setResult({
          type: "success",
          message: response.message,
          count: response.cookies_count,
        });
        message.success("认证成功！");
        autoLoginForm.resetFields();
      } else {
        setResult({
          type: "error",
          message: response.message || "登录失败",
        });
        message.error("认证失败");
      }
    } catch (error) {
      console.error("Auto login error:", error);
      const errorMsg =
        error.response?.data?.message || error.message || "网络错误";
      setResult({
        type: "error",
        message: errorMsg,
      });
      message.error("认证失败");
    } finally {
      setAutoLoginLoading(false);
    }
  };

  // Cookie上传处理
  const handleUploadCookies = async (values) => {
    setUploadLoading(true);
    setResult(null);

    try {
      const response = await uploadXCookies({
        cookies: values.cookies,
      });

      if (response.success) {
        setResult({
          type: "success",
          message: response.message,
          count: response.cookies_count,
        });
        message.success("上传成功！");
        cookieForm.resetFields();
      } else {
        setResult({
          type: "error",
          message: response.message || "上传失败",
        });
        message.error("上传失败");
      }
    } catch (error) {
      console.error("Upload cookies error:", error);
      const errorMsg =
        error.response?.data?.message || error.message || "上传失败";
      setResult({
        type: "error",
        message: errorMsg,
      });
      message.error("上传失败");
    } finally {
      setUploadLoading(false);
    }
  };

  const tabItems = [
    {
      key: "auto-login",
      label: (
        <span>
          <LoginOutlined /> 自动登录
        </span>
      ),
      children: (
        <Card>
          <Space direction="vertical" size="middle" style={{ width: "100%" }}>
            <Alert
              message="适用于有用户名和密码的用户"
              description="系统会自动在服务器上打开浏览器登录X.com并保存cookies"
              type="info"
              showIcon
            />

            <Form
              form={autoLoginForm}
              layout="vertical"
              onFinish={handleAutoLogin}
              initialValues={{ headless: true }}
            >
              <Form.Item
                label="X.com 用户名"
                name="username"
                rules={[{ required: true, message: "请输入用户名" }]}
              >
                <Input
                  prefix={<UserOutlined />}
                  placeholder="邮箱/用户名/手机号"
                  size="large"
                  disabled={autoLoginLoading}
                />
              </Form.Item>

              <Form.Item
                label="密码"
                name="password"
                rules={[{ required: true, message: "请输入密码" }]}
              >
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="X.com密码"
                  size="large"
                  disabled={autoLoginLoading}
                />
              </Form.Item>

              <Form.Item
                label="后台模式"
                name="headless"
                valuePropName="checked"
              >
                <Switch
                  checkedChildren="开启"
                  unCheckedChildren="关闭"
                  disabled={autoLoginLoading}
                />
                <Text type="secondary" style={{ marginLeft: 8 }}>
                  开启后不显示浏览器窗口
                </Text>
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  icon={<LoginOutlined />}
                  loading={autoLoginLoading}
                  size="large"
                  block
                >
                  {autoLoginLoading
                    ? "正在登录（约2-3分钟）..."
                    : "开始自动登录"}
                </Button>
              </Form.Item>
            </Form>
          </Space>
        </Card>
      ),
    },
    {
      key: "upload-cookies",
      label: (
        <span>
          <CloudUploadOutlined /> 上传Cookies
        </span>
      ),
      children: (
        <Card>
          <Space direction="vertical" size="middle" style={{ width: "100%" }}>
            <Alert
              message="适用于Google登录等OAuth场景"
              description={
                <div>
                  <div>1. 在浏览器手动登录X.com（使用Google等方式）</div>
                  <div>2. 安装Cookie-Editor扩展并导出cookies</div>
                  <div>3. 粘贴JSON格式的cookies到下方文本框</div>
                </div>
              }
              type="info"
              showIcon
            />

            <Form
              form={cookieForm}
              layout="vertical"
              onFinish={handleUploadCookies}
            >
              <Form.Item
                label="Cookies JSON"
                name="cookies"
                rules={[
                  { required: true, message: "请粘贴cookies" },
                  {
                    validator: (_, value) => {
                      if (!value) return Promise.resolve();
                      try {
                        const parsed = JSON.parse(value);
                        if (!Array.isArray(parsed)) {
                          return Promise.reject(
                            new Error("Cookies应为JSON数组")
                          );
                        }
                        return Promise.resolve();
                      } catch (e) {
                        return Promise.reject(new Error("JSON格式错误"));
                      }
                    },
                  },
                ]}
              >
                <TextArea
                  rows={10}
                  placeholder={`粘贴从Cookie-Editor导出的JSON，格式如下：
[
  {
    "name": "auth_token",
    "value": "xxxxx...",
    "domain": ".x.com",
    "path": "/",
    ...
  },
  ...
]`}
                  disabled={uploadLoading}
                />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  icon={<FileTextOutlined />}
                  loading={uploadLoading}
                  size="large"
                  block
                >
                  {uploadLoading ? "上传中..." : "验证并上传"}
                </Button>
              </Form.Item>
            </Form>
          </Space>
        </Card>
      ),
    },
  ];

  return (
    <div style={{ padding: "24px", maxWidth: "800px", margin: "0 auto" }}>
      <Title level={2}>
        <LoginOutlined /> X.com 认证设置
      </Title>
      <Text type="secondary">配置认证信息以访问完整推文时间线</Text>

      <div style={{ marginTop: "24px" }}>
        <Tabs items={tabItems} defaultActiveKey="upload-cookies" />
      </div>

      {result && (
        <Alert
          message={result.type === "success" ? "操作成功" : "操作失败"}
          description={
            <div>
              <div>{result.message}</div>
              {result.count && (
                <div style={{ marginTop: 8 }}>
                  <strong>已保存 {result.count} 个cookies</strong>
                </div>
              )}
              {result.type === "success" && (
                <div style={{ marginTop: 8 }}>
                  <strong>下一步：</strong>返回账户管理，点击"取得最新10条"测试
                </div>
              )}
            </div>
          }
          type={result.type}
          showIcon
          closable
          onClose={() => setResult(null)}
          style={{ marginTop: "16px" }}
        />
      )}

      <Card style={{ marginTop: "24px" }} size="small">
        <Space direction="vertical" size="small">
          <Text strong>📋 Cookie导出工具推荐</Text>
          <Text>• Cookie-Editor (Chrome扩展商店)</Text>
          <Text>• EditThisCookie</Text>
          <Text type="secondary" style={{ fontSize: "12px" }}>
            💡 Cookies有效期约30-90天，过期后需重新设置
          </Text>
        </Space>
      </Card>
    </div>
  );
}

export default SettingsPage;
