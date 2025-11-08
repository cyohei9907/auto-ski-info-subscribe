import React, { useState } from "react";
import {
  Card,
  Input,
  Button,
  message,
  Spin,
  Typography,
  Space,
  Divider,
} from "antd";
import {
  GlobalOutlined,
  DownloadOutlined,
  EyeOutlined,
} from "@ant-design/icons";
import { debugScrapeUrl } from "../services/api";

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

function DebugScrapePage() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleScrape = async () => {
    if (!url.trim()) {
      message.warning("请输入要抓取的URL");
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await debugScrapeUrl(url);

      if (response.success) {
        message.success(response.message);
        setResult(response);
      } else {
        message.error(response.message || "抓取失败");
      }
    } catch (error) {
      console.error("Scrape error:", error);
      message.error(error.response?.data?.message || "抓取请求失败");
    } finally {
      setLoading(false);
    }
  };

  const handleViewHtml = () => {
    if (result && result.debug_filename) {
      // 打开新窗口显示HTML
      const filename = result.debug_filename;
      // 需要创建一个新的端点来查看自定义调试文件
      window.open(`/api/monitor/debug/custom-html/${filename}/`, "_blank");
    }
  };

  const handleDownloadHtml = async () => {
    if (result && result.debug_filename) {
      const filename = result.debug_filename;
      try {
        message.loading("正在准备下载...", 0);

        // 使用 fetch 获取文件内容
        const response = await fetch(
          `/api/monitor/debug/custom-html/${filename}/?download=true`,
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
        message.error("下载失败：" + error.message);
        console.error("Download error:", error);
      }
    }
  };

  const formatBytes = (bytes) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + " KB";
    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
  };

  return (
    <div style={{ padding: "24px" }}>
      <Card>
        <Title level={2}>
          <GlobalOutlined /> 调试抓取工具
        </Title>
        <Paragraph type="secondary">
          使用已上传的Cookie登录后访问任意URL并抓取HTML内容，用于调试和分析。
        </Paragraph>

        <Divider />

        <Space direction="vertical" style={{ width: "100%" }} size="large">
          <div>
            <Text strong>输入URL：</Text>
            <Input
              size="large"
              placeholder="例如：https://x.com/elonmusk 或 x.com/elonmusk"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onPressEnter={handleScrape}
              prefix={<GlobalOutlined />}
              disabled={loading}
              style={{ marginTop: "8px" }}
            />
          </div>

          <Button
            type="primary"
            size="large"
            loading={loading}
            onClick={handleScrape}
            disabled={!url.trim()}
            block
          >
            {loading ? "正在抓取..." : "开始抓取"}
          </Button>

          {loading && (
            <div style={{ textAlign: "center", padding: "20px" }}>
              <Spin size="large" />
              <div style={{ marginTop: "16px" }}>
                <Text type="secondary">正在使用Cookie登录并抓取页面...</Text>
              </div>
            </div>
          )}

          {result && (
            <Card
              title="抓取结果"
              type="inner"
              style={{ backgroundColor: "#f0f2f5" }}
            >
              <Space
                direction="vertical"
                style={{ width: "100%" }}
                size="middle"
              >
                <div>
                  <Text strong>URL：</Text>
                  <div style={{ marginTop: "4px" }}>
                    <Text copyable>{result.url}</Text>
                  </div>
                </div>

                <div>
                  <Text strong>HTML大小：</Text>
                  <div style={{ marginTop: "4px" }}>
                    <Text>{formatBytes(result.html_size)}</Text>
                  </div>
                </div>

                <div>
                  <Text strong>保存文件名：</Text>
                  <div style={{ marginTop: "4px" }}>
                    <Text code copyable>
                      {result.debug_filename}
                    </Text>
                  </div>
                </div>

                <div>
                  <Text strong>HTML预览（前1000字符）：</Text>
                  <TextArea
                    value={result.html_preview}
                    rows={10}
                    readOnly
                    style={{
                      marginTop: "8px",
                      fontFamily: "monospace",
                      fontSize: "12px",
                    }}
                  />
                </div>

                <Space style={{ marginTop: "16px" }}>
                  <Button
                    type="primary"
                    icon={<EyeOutlined />}
                    onClick={handleViewHtml}
                  >
                    在浏览器中查看
                  </Button>
                  <Button
                    icon={<DownloadOutlined />}
                    onClick={handleDownloadHtml}
                  >
                    下载HTML文件
                  </Button>
                </Space>
              </Space>
            </Card>
          )}
        </Space>

        <Divider />

        <div style={{ marginTop: "24px" }}>
          <Title level={4}>使用说明：</Title>
          <ol style={{ paddingLeft: "20px" }}>
            <li>输入任意X.com的URL（例如：用户主页、推文详情页等）</li>
            <li>点击"开始抓取"，系统将使用已上传的Cookie登录</li>
            <li>抓取完成后，可以查看HTML内容或下载文件</li>
            <li>这个工具可以帮助您诊断为什么某些页面抓取不到推文</li>
          </ol>

          <Paragraph type="warning" style={{ marginTop: "16px" }}>
            <strong>注意：</strong>
            请确保已在"账户管理"页面上传Cookie，否则无法使用此功能。
          </Paragraph>
        </div>
      </Card>
    </div>
  );
}

export default DebugScrapePage;
