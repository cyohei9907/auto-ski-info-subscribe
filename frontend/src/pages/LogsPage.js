import React from 'react';
import { Card, Table, Tag, Typography, Button } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { useQuery, useQueryClient } from 'react-query';
import { monitorAPI } from '../services/api';

const { Title } = Typography;

const LogsPage = () => {
  const queryClient = useQueryClient();
  
  const { data: logs, isLoading } = useQuery('logs', monitorAPI.getLogs);

  const getResultColor = (result) => {
    switch (result) {
      case 'success': return 'green';
      case 'error': return 'red';
      case 'no_new_tweets': return 'orange';
      default: return 'default';
    }
  };

  const getResultText = (result) => {
    switch (result) {
      case 'success': return '成功';
      case 'error': return 'エラー';
      case 'no_new_tweets': return '新規ツイートなし';
      default: return result;
    }
  };

  const columns = [
    {
      title: 'アカウント',
      dataIndex: 'x_account_username',
      render: (username) => `@${username}`,
    },
    {
      title: '結果',
      dataIndex: 'result',
      width: 150,
      render: (result) => (
        <Tag color={getResultColor(result)}>
          {getResultText(result)}
        </Tag>
      ),
    },
    {
      title: '取得ツイート数',
      dataIndex: 'tweets_found',
      width: 120,
      align: 'center',
    },
    {
      title: '実行時間',
      dataIndex: 'execution_time',
      width: 120,
      render: (time) => `${time.toFixed(2)}秒`,
    },
    {
      title: 'エラーメッセージ',
      dataIndex: 'error_message',
      ellipsis: true,
      render: (message) => message || '-',
    },
    {
      title: '実行日時',
      dataIndex: 'created_at',
      width: 180,
      render: (created_at) => new Date(created_at).toLocaleString('ja-JP'),
    },
  ];

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Title level={2} style={{ margin: 0 }}>
              監視ログ
            </Title>
            <p style={{ margin: '8px 0 0 0', color: '#666' }}>
              アカウント監視の実行履歴とエラー情報
            </p>
          </div>
          <Button
            icon={<ReloadOutlined />}
            onClick={() => queryClient.invalidateQueries('logs')}
            loading={isLoading}
          >
            更新
          </Button>
        </div>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={Array.isArray(logs?.data) ? logs.data : []}
          loading={isLoading}
          rowKey="id"
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} / ${total} 件`,
          }}
          expandable={{
            expandedRowRender: (record) => (
              record.error_message ? (
                <div style={{ margin: 0 }}>
                  <strong>エラー詳細:</strong>
                  <pre style={{ 
                    background: '#f5f5f5', 
                    padding: 12, 
                    marginTop: 8,
                    borderRadius: 4,
                    fontSize: '12px'
                  }}>
                    {record.error_message}
                  </pre>
                </div>
              ) : null
            ),
            rowExpandable: (record) => !!record.error_message,
          }}
        />
      </Card>
    </div>
  );
};

export default LogsPage;