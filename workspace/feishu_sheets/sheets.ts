import * as Lark from "@larksuiteoapi/node-sdk";
import { Type } from "@sinclair/typebox";
import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { createFeishuClient } from "./client.js";

// ============ Schema Definitions ============

const FeishuSheetsParams = Type.Object({
  action: Type.Union([
    Type.Literal("create"),
    Type.Literal("read"),
    Type.Literal("update"),
    Type.Literal("append"),
    Type.Literal("list")
  ]),
  spreadsheetToken: Type.Optional(Type.String()),
  title: Type.Optional(Type.String()),
  folderToken: Type.Optional(Type.String()),
  sheetId: Type.Optional(Type.String()),
  range: Type.Optional(Type.String()),
  values: Type.Optional(Type.Array(Type.Array(Type.Any()))),
  limit: Type.Optional(Type.Number({ minimum: 1, maximum: 100 })),
});

type FeishuSheetsParams = typeof FeishuSheetsParams.static;

// ============ Helper Functions ============

/**
 * 创建电子表格
 */
async function createSpreadsheet(
  client: Lark.Client,
  title: string,
  folderToken?: string
): Promise<{ spreadsheetToken: string; url: string; title: string }> {
  const request: any = {
    title,
  };

  if (folderToken) {
    request.folder_token = folderToken;
  }

  const res = await client.sheets.v3.spreadsheet.create({
    data: request,
  });

  if (res.code !== 0) {
    throw new Error(`创建电子表格失败: ${res.msg}`);
  }

  return {
    spreadsheetToken: res.data.spreadsheet!.spreadsheetToken!,
    url: res.data.spreadsheet!.url!,
    title: res.data.spreadsheet!.title!,
  };
}

/**
 * 读取电子表格信息
 */
async function readSpreadsheet(
  client: Lark.Client,
  spreadsheetToken: string
): Promise<any> {
  const res = await client.sheets.v3.spreadsheet.get({
    path: { spreadsheetToken },
  });

  if (res.code !== 0) {
    throw new Error(`读取电子表格失败: ${res.msg}`);
  }

  return res.data;
}

/**
 * 获取工作表列表
 */
async function listSheets(
  client: Lark.Client,
  spreadsheetToken: string
): Promise<any[]> {
  const res = await client.sheets.v3.spreadsheet.get({
    path: { spreadsheetToken },
    params: { extFields: "sheets" },
  });

  if (res.code !== 0) {
    throw new Error(`获取工作表列表失败: ${res.msg}`);
  }

  return res.data.spreadsheet?.sheets || [];
}

/**
 * 读取单元格数据
 */
async function readCells(
  client: Lark.Client,
  spreadsheetToken: string,
  range: string
): Promise<any[][]> {
  const res = await client.sheets.v3.spreadsheetRange.get({
    path: { spreadsheetToken, range },
  });

  if (res.code !== 0) {
    throw new Error(`读取单元格数据失败: ${res.msg}`);
  }

  return res.data.values || [];
}

/**
 * 写入单元格数据
 */
async function writeCells(
  client: Lark.Client,
  spreadsheetToken: string,
  range: string,
  values: any[][]
): Promise<void> {
  const res = await client.sheets.v3.spreadsheetRange.put({
    path: { spreadsheetToken, range },
    data: { values },
  });

  if (res.code !== 0) {
    throw new Error(`写入单元格数据失败: ${res.msg}`);
  }
}

/**
 * 追加行数据
 */
async function appendRows(
  client: Lark.Client,
  spreadsheetToken: string,
  range: string,
  values: any[][]
): Promise<void> {
  const res = await client.sheets.v3.spreadsheetRange.append({
    path: { spreadsheetToken, range },
    data: { values },
  });

  if (res.code !== 0) {
    throw new Error(`追加行数据失败: ${res.msg}`);
  }
}

/**
 * 创建任务管理表格
 */
async function createTaskManagementSpreadsheet(
  client: Lark.Client,
  title: string = "OpenClaw任务管理",
  folderToken?: string
): Promise<{ spreadsheetToken: string; url: string }> {
  // 1. 创建电子表格
  const spreadsheet = await createSpreadsheet(client, title, folderToken);
  
  // 2. 创建工作表
  const sheets = [
    { title: "任务清单", index: 0 },
    { title: "团队成员", index: 1 },
    { title: "统计看板", index: 2 },
    { title: "时间效率", index: 3 }
  ];

  // 3. 初始化任务清单表头
  const taskHeaders = [
    ["任务ID", "任务名称", "状态", "优先级", "负责人", "创建时间", "预计完成", "实际完成", "耗时(分钟)", "描述", "产出"]
  ];
  
  await writeCells(client, spreadsheet.spreadsheetToken, "任务清单!A1:K1", taskHeaders);

  // 4. 初始化团队成员表头
  const teamHeaders = [
    ["成员", "角色", "擅长领域", "当前任务", "状态", "已完成任务数", "专长分类"]
  ];
  
  await writeCells(client, spreadsheet.spreadsheetToken, "团队成员!A1:G1", teamHeaders);

  // 5. 初始化统计看板
  const dashboardHeaders = [
    ["统计项", "数值", "单位", "说明"],
    ["总任务数", "=COUNTA(任务清单!A:A)-1", "个", "所有任务数量"],
    ["已完成", "=COUNTIF(任务清单!C:C,\"已完成\")", "个", "已完成任务数量"],
    ["进行中", "=COUNTIF(任务清单!C:C,\"进行中\")", "个", "进行中任务数量"],
    ["完成率", "=已完成/总任务数", "%", "任务完成比例"],
    ["总耗时", "=SUM(任务清单!I:I)", "分钟", "所有任务总耗时"],
    ["平均耗时", "=总耗时/总任务数", "分钟", "平均每个任务耗时"]
  ];
  
  await writeCells(client, spreadsheet.spreadsheetToken, "统计看板!A1:D7", dashboardHeaders);

  return spreadsheet;
}

// ============ Main Tool Function ============

export async function feishuSheetsTool(
  api: OpenClawPluginApi,
  params: FeishuSheetsParams
): Promise<any> {
  try {
    // 获取飞书客户端
    const client = createFeishuClient({});

    switch (params.action) {
      case "create":
        if (!params.title) {
          throw new Error("创建电子表格需要title参数");
        }
        return await createSpreadsheet(client, params.title, params.folderToken);

      case "read":
        if (!params.spreadsheetToken) {
          throw new Error("读取电子表格需要spreadsheetToken参数");
        }
        return await readSpreadsheet(client, params.spreadsheetToken);

      case "update":
        if (!params.spreadsheetToken || !params.range || !params.values) {
          throw new Error("更新单元格需要spreadsheetToken、range和values参数");
        }
        await writeCells(client, params.spreadsheetToken, params.range, params.values);
        return { success: true, message: "单元格更新成功" };

      case "append":
        if (!params.spreadsheetToken || !params.range || !params.values) {
          throw new Error("追加行需要spreadsheetToken、range和values参数");
        }
        await appendRows(client, params.spreadsheetToken, params.range, params.values);
        return { success: true, message: "行数据追加成功" };

      case "list":
        if (!params.spreadsheetToken) {
          throw new Error("列出工作表需要spreadsheetToken参数");
        }
        return await listSheets(client, params.spreadsheetToken);

      default:
        throw new Error(`未知的action: ${params.action}`);
    }
  } catch (error: any) {
    return {
      error: error.message,
      stack: error.stack,
    };
  }
}

// ============ Plugin Registration ============

export const feishuSheetsPlugin = {
  name: "feishu_sheets",
  tools: [
    {
      name: "feishu_sheets",
      description: "飞书电子表格操作工具",
      parameters: FeishuSheetsParams,
      handler: feishuSheetsTool,
    },
  ],
};