import { test, expect } from '@playwright/test';
import { loginAsAdmin, loginAsEntry, randomName } from './helpers';

test.describe('用户管理模块测试', () => {
  test.describe.serial('管理员操作', () => {
    test.beforeEach(async ({ page }) => {
      await loginAsAdmin(page);
    });

    test('U01 - 列表显示用户', async ({ page }) => {
      await page.goto('/users');

      // 验证用户列表显示
      await expect(page.locator('.el-table').first()).toBeVisible({ timeout: 10000 });
    });

    test('U02 - 创建用户', async ({ page }) => {
      await page.goto('/users');

      // 等待页面加载
      await page.waitForTimeout(1000);

      // 点击新建用户按钮
      await page.click('button:has-text("新建用户")');

      // 等待对话框
      const dialog = page.locator('.el-dialog');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // 填写用户名
      const username = randomName('testuser');
      await dialog.locator('input[placeholder*="用户名"]').fill(username);

      // 填写密码
      await dialog.locator('input[placeholder*="密码"]').fill('Test123456');

      // 选择角色
      const roleSelect = dialog.locator('.el-select').first();
      await roleSelect.click();
      await page.waitForTimeout(300);
      await page.locator('.el-select-dropdown:visible .el-select-dropdown__item').first().click();

      // 选择堂区（如果需要）
      const villageSelect = dialog.locator('.el-select').nth(1);
      if (await villageSelect.isVisible({ timeout: 500 })) {
        await villageSelect.click();
        await page.waitForTimeout(300);
        await page.locator('.el-select-dropdown:visible .el-select-dropdown__item').first().click();
      }

      // 保存
      await dialog.locator('button:has-text("确定")').click();

      // 验证创建成功
      await expect(page.locator('.el-message--success')).toBeVisible({ timeout: 5000 });
    });

    test('U03 - 编辑用户', async ({ page }) => {
      await page.goto('/users');

      // 等待表格加载
      await page.waitForSelector('.el-table', { timeout: 10000 });
      await page.waitForTimeout(1000);

      // 确保有用户数据可以编辑
      let editButton = page.locator('.el-table button:has-text("编辑")').first();

      if (!await editButton.isVisible({ timeout: 2000 })) {
        // 创建一个用户
        await page.click('button:has-text("新建用户")');
        const dialog = page.locator('.el-dialog');
        await expect(dialog).toBeVisible({ timeout: 5000 });
        await dialog.locator('input[placeholder*="用户名"]').fill(randomName('待编辑'));
        await dialog.locator('input[placeholder*="密码"]').fill('Test123456');
        const roleSelect = dialog.locator('.el-select').first();
        await roleSelect.click();
        await page.waitForTimeout(300);
        await page.locator('.el-select-dropdown:visible .el-select-dropdown__item').first().click();
        await dialog.locator('button:has-text("确定")').click();
        await expect(page.locator('.el-message--success')).toBeVisible({ timeout: 5000 });

        await page.reload();
        await page.waitForSelector('.el-table', { timeout: 10000 });
        await page.waitForTimeout(1000);
        editButton = page.locator('.el-table button:has-text("编辑")').first();
      }

      // 点击编辑按钮
      await editButton.click();

      // 等待对话框
      const dialog = page.locator('.el-dialog');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // 保存
      await dialog.locator('button:has-text("确定")').click();

      // 验证修改成功
      await expect(page.locator('.el-message--success')).toBeVisible({ timeout: 5000 });
    });

    test('U04 - 重置密码', async ({ page }) => {
      await page.goto('/users');

      // 等待表格加载
      await page.waitForSelector('.el-table', { timeout: 10000 });
      await page.waitForTimeout(1000);

      // 找到重置密码按钮（点击第二个用户的，避免是admin）
      const resetButton = page.locator('.el-table button:has-text("重置密码")').nth(1);
      await expect(resetButton).toBeVisible({ timeout: 5000 });

      // 点击重置密码按钮
      await resetButton.click();

      // 等待重置密码对话框
      const resetDialog = page.locator('.el-dialog');
      await expect(resetDialog).toBeVisible({ timeout: 5000 });

      // 输入新密码 - 使用精确placeholder定位
      const passwordInput = resetDialog.locator('input[placeholder="请输入新密码"]');
      await passwordInput.fill('NewPass123');

      // 输入确认密码
      const confirmInput = resetDialog.locator('input[placeholder="请再次输入新密码"]');
      await confirmInput.fill('NewPass123');

      // 确认
      await resetDialog.locator('button:has-text("确定")').click();

      // 验证成功
      await expect(page.locator('.el-message--success')).toBeVisible({ timeout: 5000 });
    });
  });

  test('U05 - 录入员无用户管理权限', async ({ page }) => {
    await loginAsEntry(page);
    await page.goto('/users');

    // 验证重定向到仪表盘或显示无权限
    await page.waitForTimeout(2000);
    const currentUrl = page.url();

    // 应该被重定向到仪表盘
    expect(currentUrl).not.toContain('/users');
  });
});
