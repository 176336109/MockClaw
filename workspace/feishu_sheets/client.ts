import * as Lark from "@larksuiteoapi/node-sdk";

// 复用现有的client逻辑
export type FeishuClientCredentials = {
  accountId?: string;
  appId?: string;
  appSecret?: string;
  domain?: string;
};

// 客户端缓存
const clientCache = new Map<
  string,
  {
    client: Lark.Client;
    config: { appId: string; appSecret: string; domain?: string };
  }
>();

function resolveDomain(domain: string | undefined): Lark.Domain | string {
  if (domain === "lark") {
    return Lark.Domain.Lark;
  }
  if (domain === "feishu" || !domain) {
    return Lark.Domain.Feishu;
  }
  return domain.replace(/\/+$/, "");
}

/**
 * 创建飞书客户端
 * 这里简化处理，使用默认配置
 */
export function createFeishuClient(creds: FeishuClientCredentials = {}): Lark.Client {
  const { accountId = "default" } = creds;

  // 检查缓存
  const cached = clientCache.get(accountId);
  if (cached) {
    return cached.client;
  }

  // 这里需要从OpenClaw配置中获取appId和appSecret
  // 暂时使用默认值，实际使用时需要从配置读取
  const appId = process.env.FEISHU_APP_ID || "";
  const appSecret = process.env.FEISHU_APP_SECRET || "";
  const domain = process.env.FEISHU_DOMAIN as "feishu" | "lark" | undefined;

  if (!appId || !appSecret) {
    throw new Error("飞书应用配置未找到，请设置FEISHU_APP_ID和FEISHU_APP_SECRET环境变量");
  }

  // 创建新客户端
  const client = new Lark.Client({
    appId,
    appSecret,
    appType: Lark.AppType.SelfBuild,
    domain: resolveDomain(domain),
  });

  // 缓存
  clientCache.set(accountId, {
    client,
    config: { appId, appSecret, domain },
  });

  return client;
}