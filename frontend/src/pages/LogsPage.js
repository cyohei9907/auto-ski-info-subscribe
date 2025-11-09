import React from "react";
import { Card, Table, Tag, Typography, Button } from "antd";
import { ReloadOutlined } from "@ant-design/icons";
import { useQuery, useQueryClient } from "react-query";
import { monitorAPI } from "../services/api";

const { Title } = Typography;

const LogsPage = () => {
  const queryClient = useQueryClient();

  const { data: logs, isLoading, error } = useQuery("logs", monitorAPI.getLogs);

  // デバッグログ
  console.log("=== LogsPage Debug Logs ===");
  console.log("Raw logs data:", logs);
  console.log("Is loading:", isLoading);
  console.log("Error:", error);

  const logsData = Array.isArray(logs?.data) ? logs.data : [];
  console.log("Parsed logsData:", logsData);
  console.log("Logs count:", logsData.length);
  console.log("=== End Debug Logs ===");

  const getResultColor = (result) => {
    switch (result) {
      case "success":
        return "green";
      case "error":
        return "red";
      case "no_new_tweets":
        return "orange";
      default:
        return "default";
    }
  };

  const getResultText = (result) => {
    switch (result) {
      case "success":
        return "成功";
      case "error":
        return "エラー";
      case "no_new_tweets":
        return "新規ツイートなし";
      default:
        return result;
    }
  };

  const columns = [
    {
      title: "アカウント",
      dataIndex: "x_account_username",
      width: 120,
      fixed: "left",
      render: (username) => `@${username}`,
    },
    {
      title: "結果",
      dataIndex: "result",
      width: 120,
      render: (result) => (
        <Tag color={getResultColor(result)}>{getResultText(result)}</Tag>
      ),
    },
    {
      title: "ツイート数",
      dataIndex: "tweets_found",
      width: 100,
      align: "center",
    },
    {
      title: "実行時間",
      dataIndex: "execution_time",
      width: 100,
      render: (time) => `${time.toFixed(2)}秒`,
    },
    {
      title: "エラー",
      dataIndex: "error_message",
      width: 200,
      ellipsis: true,
      render: (message) => message || "-",
    },
    {
      title: "実行日時",
      dataIndex: "created_at",
      width: 150,
      render: (created_at) =>
        new Date(created_at).toLocaleString("ja-JP", {
          month: "2-digit",
          day: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
        }),
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
              監視ログ
            </Title>
            <p style={{ margin: "8px 0 0 0", color: "#666" }}>
              アカウント監視の実行履歴とエラー情報
            </p>
          </div>
          <Button
            icon={<ReloadOutlined />}
            onClick={() => queryClient.invalidateQueries("logs")}
            loading={isLoading}
          >
            更新
          </Button>
        </div>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={logsData}
          loading={isLoading}
          rowKey="id"
          scroll={{ x: 800 }}
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} / ${total} 件`,
            responsive: true,
          }}
          expandable={{
            expandedRowRender: (record) =>
              record.error_message ? (
                <div style={{ margin: 0 }}>
                  <strong>エラー詳細:</strong>
                  <pre
                    style={{
                      background: "#f5f5f5",
                      padding: 12,
                      marginTop: 8,
                      borderRadius: 4,
                      fontSize: "12px",
                      overflow: "auto",
                      maxWidth: "100%",
                    }}
                  >
                    {record.error_message}
                  </pre>
                </div>
              ) : null,
            rowExpandable: (record) => !!record.error_message,
          }}
        />
      </Card>
    </div>
  );
};

export default LogsPage;
