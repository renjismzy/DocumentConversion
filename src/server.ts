import { ContextInjected, TcbExtendedContext } from '@cloudbase/functions-typings';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import tcb from '@cloudbase/node-sdk';
import { z } from 'zod';

export function createServer(context: ContextInjected<TcbExtendedContext>) {
  const server = new McpServer(
    {
      name: 'Basic Server',
      version: '1.0.0',
    },
    { capabilities: { tools: {} } },
  );

  const env = context.extendedContext?.envId || process.env.CLOUDBASE_ENVIRONMENT; // 本地开发从环境变量读
  const secretId = context.extendedContext?.tmpSecret?.secretId;
  const secretKey = context.extendedContext?.tmpSecret?.secretKey;
  const sessionToken = context.extendedContext?.tmpSecret?.token;

  // 创建 Cloudbase Node sdk 实例
  const app = tcb.init({
    env,
    secretId,
    secretKey,
    sessionToken,
  });

  server.registerTool(
    'getUserVisitInfo',
    {
      description: '获取最新的用户访问信息',
      inputSchema: {
        count: z.number().describe('获取最近 {count} 条用户访问信息'),
      },
      outputSchema: {
        total: z.number().describe('数据模型中总共的用户访问信息数量'),
        records: z
          .array(
            z.object({
              device: z.string().describe('用户设备'),
              visitTime: z.number().describe('用户访问时间'),
            }),
          )
          .describe('返回的用户访问信息数组'),
      },
    },
    async ({ count }) => {
      const res = await app.models.sys_user_dau.list({
        pageSize: count,
        getCount: true,
        orderBy: [
          {
            visit_time: 'desc',
          },
        ],
      });

      const structuredContent = {
        total: res.data.total,
        records: res.data.records.map((x) => ({
          device: x.device,
          visitTime: x.visit_time,
        })),
      };

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(structuredContent),
          },
        ],
        structuredContent,
      };
    },
  );

  server.registerTool(
    'getChatRecords',
    {
      description: '获取聊天记录',
      inputSchema: {
        count: z.number({
          description: '获取的聊天记录数量',
        }),
      },
      outputSchema: {
        total: z.number({
          description: '数据模型中总共的聊天记录数量',
        }),
        records: z.array(
          z.object({
            content: z.string({
              description: '聊天记录内容',
            }),
            role: z.string({
              description: '聊天记录角色',
            }),
          }),
          {
            description: '聊天记录',
          },
        ),
      },
    },
    async ({ count }) => {
      const res = await app.models.ai_bot_chat_history_5hobd2b.list({
        pageSize: count,
        getCount: true,
      });

      const { data } = res;

      const structuredContent = {
        total: data.total,
        records: data.records.map((x) => ({
          content: x.content,
          role: x.role,
        })),
      };

      return {
        structuredContent,
        content: [
          {
            type: 'text',
            text: JSON.stringify(structuredContent),
          },
        ],
      };
    },
  );

  return { server };
}
