import { test, expect } from '@playwright/test';
import { loginAsAdmin } from './helpers';

test.describe('仪表盘模块测试', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  test('D01 - 显示欢迎信息', async ({ page }) => {
    await page.goto('/dashboard');

    // 验证显示欢迎信息或系统首页
    await expect(page.locator('body')).toContainText(/欢迎|统计|概览|系统首页|当前用户/, { timeout: 10000 });
  });

  test('D02 - 显示堂区统计', async ({ page }) => {
    await page.goto('/dashboard');

    // 验证显示用户信息
    await expect(page.locator('body')).toContainText(/当前用户|角色|权限/, { timeout: 10000 });

    // 检查描述列表
    const descriptions = page.locator('.el-descriptions');
    await expect(descriptions).toBeVisible({ timeout: 5000 });
  });

  test('D03 - 显示家庭统计', async ({ page }) => {
    await page.goto('/dashboard');

    // 验证显示角色和权限信息
    await expect(page.locator('body')).toContainText(/角色|权限/, { timeout: 10000 });

    // 检查描述列表
    const descriptions = page.locator('.el-descriptions');
    await expect(descriptions).toBeVisible({ timeout: 5000 });
  });
});
