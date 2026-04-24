import { test, expect } from '@playwright/test';
import { loginAsAdmin } from './helpers';

test.describe('设置模块测试', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  test('ST01 - 显示数据库信息', async ({ page }) => {
    await page.goto('/settings');
    await expect(page.locator('body')).toContainText(/堂区数|家庭数|成员数/, { timeout: 10000 });
  });

  test('ST02 - 下载数据库备份', async ({ page }) => {
    await page.goto('/settings');

    const [download] = await Promise.all([
      page.waitForEvent('download', { timeout: 10000 }),
      page.getByRole('button', { name: '下载数据库备份' }).click(),
    ]);

    expect(download.suggestedFilename()).toContain('household_backup_');
  });

  test('ST03 - 显示数据库导入风险提示', async ({ page }) => {
    await page.goto('/settings');

    await expect(page.locator('body')).toContainText('导入数据库会先自动备份当前数据库');
    await expect(page.locator('body')).toContainText('导入成功后请立即重启后端服务');
  });

  test('ST04 - 选择数据库文件后弹出确认框', async ({ page }) => {
    await page.goto('/settings');

    const chooserPromise = page.waitForEvent('filechooser');
    await page.locator('button:has-text("导入数据库恢复")').click();
    const chooser = await chooserPromise;

    await chooser.setFiles({
      name: 'invalid.sqlite',
      mimeType: 'application/octet-stream',
      buffer: Buffer.from('not-a-sqlite-file'),
    });

    await expect(page.locator('.el-message-box')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('.el-message-box')).toContainText('导入数据库将覆盖当前所有数据');

    await page.locator('.el-message-box button:has-text("取消")').click();
    await expect(page.locator('.el-message-box')).toBeHidden({ timeout: 5000 });
  });
});
