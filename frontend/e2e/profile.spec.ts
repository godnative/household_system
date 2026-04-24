import { test, expect } from '@playwright/test';
import { loginAsAdmin, TEST_ACCOUNTS } from './helpers';

test.describe('个人中心模块测试', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  test('PR01 - 查看个人信息', async ({ page }) => {
    await page.goto('/profile');

    // 验证显示当前用户信息
    await expect(page.locator('body')).toContainText(/admin|用户名|角色/, { timeout: 10000 });
  });

  test('PR02 - 修改密码表单验证', async ({ page }) => {
    await page.goto('/change-password');

    // 验证表单元素存在
    await expect(page.locator('input[placeholder*="原密码"]')).toBeVisible();
    await expect(page.locator('input[placeholder="请输入新密码"]')).toBeVisible();
    await expect(page.locator('input[placeholder*="再次"]')).toBeVisible();
    await expect(page.locator('button:has-text("提交")')).toBeVisible();
  });

  test('PR03 - 修改密码错误旧密码', async ({ page }) => {
    await page.goto('/change-password');

    // 填写错误的旧密码
    await page.fill('input[placeholder*="原密码"]', 'wrongoldpass');

    // 填写新密码
    await page.fill('input[placeholder*="新密码"]', 'NewPass123');

    // 确认新密码
    await page.fill('input[placeholder*="再次"]', 'NewPass123');

    // 点击提交按钮
    await page.click('button:has-text("提交")');

    // 验证显示错误提示
    await expect(page.locator('.el-message--error, .el-alert--error')).toBeVisible({ timeout: 5000 });
  });
});
