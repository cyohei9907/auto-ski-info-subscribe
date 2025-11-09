import React, { useState, useEffect } from "react";
import { Card, Select, Button, Typography, Space, message } from "antd";
import {
  DownloadOutlined,
  EyeOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { monitorAPI } from "../services/api";

const { Title, Text } = Typography;
const { Option } = Select;

function DebugPage() {
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      const response = await monitorAPI.getAccounts();
      console.log("API Response:", response); // 调试日志
      console.log("Response data:", response.data); // 调试日志
      // 确保 accounts 是数组
      const accountsData = Array.isArray(response.data) ? response.data : [];
      console.log("Accounts data:", accountsData); // 调试日志
      setAccounts(accountsData);
      // 只在成功加载后才显示消息，不要在加载时就显示警告
      if (accountsData.length > 0) {
        // 不显示消息，静默加载
        console.log(`加载了 ${accountsData.length} 个账号`);
      }
    } catch (error) {
      console.error("Load accounts error:", error); // 调试日志
      message.error(
        "加载账号失败: " + (error.response?.data?.message || error.message)
      );
      setAccounts([]); // 出错时设置为空数组
    }
  };

  const handleViewHTML = async () => {
    if (!selectedAccount) {
      message.warning("请先选择账号");
      return;
    }

    const account = accounts.find((a) => a.id === selectedAccount);
    if (!account) return;

    setLoading(true);
    try {
      // 直接在新窗口打开HTML
      const url = `/api/monitor/debug/html/${account.username}/`;
      window.open(url, "_blank");
      message.success("已在新窗口打开调试HTML");
    } catch (error) {
      message.error(
        "加载HTML失败: " + (error.response?.data?.message || error.message)
      );
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadHTML = async () => {
    if (!selectedAccount) {
      message.warning("请先选择账号");
      return;
    }

    const account = accounts.find((a) => a.id === selectedAccount);
    if (!account) return;

    setLoading(true);
    try {
      message.loading("正在准备下载...", 0);

      // 使用 fetch 获取文件
      const response = await fetch(
        `/api/monitor/debug/html/${account.username}/?download=true`,
        {
          headers: {
            Authorization: `Token ${localStorage.getItem("token")}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("下载失败");
      }

      // 获取 blob 数据
      const blob = await response.blob();
      const filename = `twitter_${account.username}_debug.html`;

      // 创建下载链接
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      link.style.display = "none";
      document.body.appendChild(link);
      link.click();

      // 清理
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      message.destroy();
      message.success("HTML文件下载成功");
    } catch (error) {
      message.destroy();
      message.error(
        "下载失败: " + (error.response?.data?.message || error.message)
      );
    } finally {
      setLoading(false);
    }
  };

  const handleFetchLatest = async () => {
    if (!selectedAccount) {
      message.warning("请先选择账号");
      return;
    }

    setLoading(true);
    try {
      const response = await monitorAPI.fetchLatestTweets(selectedAccount);
      message.success(response.data.message || "抓取成功");
    } catch (error) {
      message.error(
        "抓取失败: " + (error.response?.data?.message || error.message)
      );
    } finally {
      setLoading(false);
    }
  };

  const selectedAccountData = Array.isArray(accounts)
    ? accounts.find((a) => a.id === selectedAccount)
    : null;

  return (
    <div style={{ padding: "24px" }}>
      <Card>
        <Title level={2}>🔍 爬虫调试工具</Title>
        <Text type="secondary">
          查看和下载爬虫抓取的原始HTML，用于调试和分析X.com返回的内容
        </Text>

        <div style={{ marginTop: "24px" }}>
          <Space direction="vertical" size="large" style={{ width: "100%" }}>
            <div>
              <Text strong>选择X.com账号：</Text>
              <Select
                placeholder={
                  accounts.length === 0
                    ? "没有账号，请先在账号管理页面添加"
                    : "选择要调试的账号"
                }
                style={{ width: "400px", marginLeft: "12px" }}
                value={selectedAccount}
                onChange={setSelectedAccount}
                disabled={accounts.length === 0}
              >
                {accounts.map((account) => (
                  <Option key={account.id} value={account.id}>
                    @{account.username}
                  </Option>
                ))}
              </Select>
            </div>

            {accounts.length === 0 && (
              <Card type="inner">
                <Text type="secondary">
                  ℹ️ 还没有添加任何X.com账号。请前往
                  <a href="/accounts">账号管理</a>页面添加账号。
                </Text>
              </Card>
            )}

            {selectedAccountData && (
              <Card type="inner" title="操作步骤">
                <Space
                  direction="vertical"
                  size="middle"
                  style={{ width: "100%" }}
                >
                  <div>
                    <Text strong>步骤 1: 抓取最新推文</Text>
                    <div style={{ marginTop: "8px" }}>
                      <Button
                        type="primary"
                        icon={<ReloadOutlined />}
                        onClick={handleFetchLatest}
                        loading={loading}
                      >
                        执行抓取（会保存HTML文件）
                      </Button>
                    </div>
                  </div>

                  <div>
                    <Text strong>步骤 2: 查看或下载HTML</Text>
                    <div style={{ marginTop: "8px" }}>
                      <Space>
                        <Button
                          icon={<EyeOutlined />}
                          onClick={handleViewHTML}
                          loading={loading}
                        >
                          在新窗口打开HTML
                        </Button>
                        <Button
                          icon={<DownloadOutlined />}
                          onClick={handleDownloadHTML}
                          loading={loading}
                        >
                          下载HTML文件
                        </Button>
                      </Space>
                    </div>
                  </div>

                  <Card
                    size="small"
                    style={{
                      backgroundColor: "#f6ffed",
                      border: "1px solid #b7eb8f",
                    }}
                  >
                    <Text type="success">
                      <strong>💡 使用提示：</strong>
                      <ul style={{ marginTop: "8px", paddingLeft: "20px" }}>
                        <li>先执行"抓取"操作，系统会保存X.com返回的原始HTML</li>
                        <li>然后可以在浏览器中查看或下载HTML文件进行分析</li>
                        <li>
                          检查HTML中的 <code>datetime</code>{" "}
                          属性，确认X.com实际返回了哪些日期的推文
                        </li>
                        <li>如果HTML中没有最新推文，可能需要重新上传cookie</li>
                      </ul>
                    </Text>
                  </Card>
                </Space>
              </Card>
            )}
          </Space>
        </div>
      </Card>
    </div>
  );
}

export default DebugPage;
