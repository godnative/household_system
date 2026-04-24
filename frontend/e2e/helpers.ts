import { Page } from '@playwright/test';

// 测试账号信息
export const TEST_ACCOUNTS = {
  admin: {
    username: 'admin',
    password: 'admin123',
  },
  entry: {
    username: 'test_entry',
    password: 'test123',
  },
  observer: {
    username: 'test_observer',
    password: 'test123',
  },
};

// 登录函数
export async function login(page: Page, username: string, password: string) {
  await page.goto('/login');
  await page.fill('input[placeholder="请输入用户名"]', username);
  await page.fill('input[placeholder="请输入密码"]', password);
  await page.click('button:has-text("登录")');
  // 等待登录成功跳转
  await page.waitForURL(/\/dashboard/, { timeout: 10000 });
}

// 以admin身份登录
export async function loginAsAdmin(page: Page) {
  await login(page, TEST_ACCOUNTS.admin.username, TEST_ACCOUNTS.admin.password);
}

// 以录入员身份登录
export async function loginAsEntry(page: Page) {
  await login(page, TEST_ACCOUNTS.entry.username, TEST_ACCOUNTS.entry.password);
}

// 以观察员身份登录
export async function loginAsObserver(page: Page) {
  await login(page, TEST_ACCOUNTS.observer.username, TEST_ACCOUNTS.observer.password);
}

// 登出函数
export async function logout(page: Page) {
  // 点击用户头像或菜单
  await page.click('.el-dropdown-link, [class*="user"], .el-avatar');
  // 点击登出按钮
  await page.click('text=退出登录, text=登出, text=注销');
  await page.waitForURL(/\/login/, { timeout: 10000 });
}

// 等待请求完成
export async function waitForApi(page: Page, urlPattern: string | RegExp) {
  return page.waitForResponse((response) => {
    const url = response.url();
    if (typeof urlPattern === 'string') {
      return url.includes(urlPattern);
    }
    return urlPattern.test(url);
  });
}

// 生成随机字符串
export function randomString(length: number = 6): string {
  return Math.random().toString(36).substring(2, length + 2);
}

// 生成随机名称（用于测试数据）
export function randomName(prefix: string = '测试'): string {
  return `${prefix}_${randomString(8)}`;
}
