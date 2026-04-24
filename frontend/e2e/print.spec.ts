import { test, expect } from '@playwright/test';
import { loginAsAdmin } from './helpers';

test.describe('打印模块测试', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  test('P01 - 打印页无参数时显示空状态', async ({ page }) => {
    await page.goto('/print');
    await expect(page.locator('body')).toContainText('暂无可打印内容', { timeout: 10000 });
  });

  test('P02 - 家庭联动页显示当前家庭信息', async ({ page }) => {
    await page.goto('/households');
    await page.locator('.el-table .el-table__row').first().click();
    await expect(page.locator('body')).toContainText('当前家庭：', { timeout: 10000 });
    await expect(page.locator('body')).toContainText('户主：', { timeout: 10000 });
    await expect(page.getByRole('button', { name: '新建成员' })).toBeVisible({ timeout: 10000 });
  });

  test('P03 - 打印页工具栏存在返回与导出按钮', async ({ page }) => {
    await page.goto('/print?member_id=1');
    await expect(page.getByRole('button', { name: '返回' })).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole('button', { name: '打印 / 导出 PDF' })).toBeVisible();
  });
});
