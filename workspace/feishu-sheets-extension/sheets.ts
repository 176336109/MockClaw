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
    Type.Literal("list"),
    Type.Literal("create_task_management")
  ]),
  spreadsheetToken: Type.Optional(Type.String()),
  title: Type.Optional(Type.String()),
  folderToken: Type.Optional(Type.String()),
  sheetId: Type.Optional(Type.String()),
  range: Type.Optional(Type.String()),
  values: Type.Optional(Type.Array(Type.Array(Type.Any()))),
});

type FeishuSheetsParams = typeof FeishuSheetsParams.static;

// ============ Helper Functions ============

/**
 * 创建电子表格
 */
async function createSpreadsheet(
  client: any,
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
  client: any,
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
  client: any,
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
  client: any,
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
  client: any,
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
  client: any,
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
  client: any,
  title: string = "OpenClaw任务管理",
  folderToken?: string
): Promise<{ spreadsheetToken: string; url: string }> {
  // 1. 创建电子表格
  const spreadsheet = await createSpreadsheet(client, title, folderToken);
  
  // 2. 初始化任务清单表头
  const taskHeaders = [
    ["任务ID", "任务名称", "状态", "优先级", "负责人", "创建时间", "预计完成", "实际完成", "耗时(分钟)", "描述", "产出"]
  ];
  
  await writeCells(client, spreadsheet.spreadsheetToken, "Sheet1!A1:K1", taskHeaders);

  // 3. 初始化团队成员表头
  const teamHeaders = [
    ["成员", "角色", "擅长领域", "当前任务", "状态", "已完成任务数", "专长分类"]
  ];
  
  await writeCells(client, spreadsheet.spreadsheetToken, "Sheet2!A1:G1", teamHeaders);

  // 4. 初始化统计看板
  const dashboardHeaders = [
    ["统计项", "数值", "单位", "说明"],
    ["总任务数", "=COUNTA(Sheet1!A:A)-1", "个", "所有任务数量"],
    ["已完成", "=COUNTIF(Sheet1!C:C,\"已完成\")", "个", "已完成任务数量"],
    ["进行中", "=COUNTIF(Sheet1!C:C,\"进行中\")", "个", "进行中任务数量"],
    ["完成率", "=B3/B2", "%", "任务完成比例"],
    ["总耗时", "=SUM(Sheet1!I:I)", "分钟", "所有任务总耗时"],
    ["平均耗时", "=B6/B2", "分钟", "平均每个任务耗时"]
  ];
  
  await writeCells(client, spreadsheet.spreadsheetToken, "Sheet3!A1:D7", dashboardHeaders);

  return spreadsheet;
}

// ============ Main Tool Function ============

export async function feishuSheetsTool(
  api: OpenClawPluginApi,
  params: FeishuSheetsParams
): Promise<any> {
  try {
    // 获取飞书客户端 - 复用现有的认证机制
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

      case "create_task_management":
        return await createTaskManagementSpreadsheet(client, params.title, params.folderToken);

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

export function registerFeishuSheetsTools(api: OpenClawPluginApi) {
  api.registerTool({
    name: "feishu_sheets",
    description: "飞书电子表格操作工具",
    parameters: FeishuSheetsParams,
    handler: feishuSheetsTool,
  });
}