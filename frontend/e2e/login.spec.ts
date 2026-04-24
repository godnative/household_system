import { test, expect } from '@playwright/test';
import { TEST_ACCOUNTS, loginAsAdmin, logout } from './helpers';

test.describe('登录模块测试', () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  test('L01 - 正确登录', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder="请输入用户名"]', TEST_ACCOUNTS.admin.username);
    await page.fill('input[placeholder="请输入密码"]', TEST_ACCOUNTS.admin.password);
    await page.click('button:has-text("登录")');

    // 验证跳转到仪表盘
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 });

    // 验证显示用户名
    await expect(page.locator('body')).toContainText('admin');
  });

  test('L02 - 错误密码登录', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder="请输入用户名"]', TEST_ACCOUNTS.admin.username);
    await page.fill('input[placeholder="请输入密码"]', 'wrongpass');
    await page.click('button:has-text("登录")');

    // 验证留在登录页
    await expect(page).toHaveURL(/\/login/);

    // 验证显示错误提示
    await expect(page.locator('.el-message--error, .el-alert--error')).toBeVisible({ timeout: 5000 });
  });

  test('L03 - 空用户名登录', async ({ page }) => {
    await page.goto('/login');

    // 清空用户名
    await page.fill('input[placeholder="请输入用户名"]', '');
    await page.fill('input[placeholder="请输入密码"]', TEST_ACCOUNTS.admin.password);
    await page.click('button:has-text("登录")');

    // 验证留在登录页
    await expect(page).toHaveURL(/\/login/);

    // 验证显示错误提示 (el-alert)
    await expect(page.locator('.el-alert--error')).toBeVisible({ timeout: 5000 });
  });

  test('L04 - 未认证访问保护页面', async ({ page }) => {
    await page.goto('/dashboard');

    // 验证重定向到登录页
    await expect(page).toHaveURL(/\/login/, { timeout: 10000 });
  });

  test('L05 - 登录后访问登录页', async ({ page }) => {
    await loginAsAdmin(page);

    // 访问登录页
    await page.goto('/login');

    // 验证重定向到仪表盘
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 5000 });
  });

  test('L06 - 登出', async ({ page }) => {
    await loginAsAdmin(page);

    // 等待页面加载
    await page.waitForSelector('body');

    // 点击退出登录按钮
    await page.click('text=退出登录');

    // 验证跳转到登录页
    await expect(page).toHaveURL(/\/login/, { timeout: 10000 });
  });
});
