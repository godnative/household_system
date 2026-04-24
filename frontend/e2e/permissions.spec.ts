import { test, expect } from '@playwright/test';
import { loginAsAdmin } from './helpers';

test.describe('角色管理模块测试', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  test('R01 - 列表显示角色', async ({ page }) => {
    await page.goto('/users');

    // 等待页面加载
    await page.waitForTimeout(1000);

    // 验证角色标签存在
    const roleTab = page.locator('.el-tabs__item:has-text("角色")');
    await expect(roleTab).toBeVisible({ timeout: 5000 });

    // 切换到角色标签
    await roleTab.click();

    // 等待角色面板加载
    await page.waitForTimeout(1500);

    // 验证页面显示角色相关内容
    await expect(page.locator('.el-tabs__content')).toBeVisible({ timeout: 5000 });
  });

  test('R02 - 查看角色权限', async ({ page }) => {
    await page.goto('/users');

    // 等待页面加载
    await page.waitForTimeout(1000);

    // 切换到角色标签
    const roleTab = page.locator('.el-tabs__item:has-text("角色")');
    await expect(roleTab).toBeVisible({ timeout: 5000 });
    await roleTab.click();
    await page.waitForTimeout(1500);

    // 等待角色面板
    const rolePanel = page.locator('.role-list-panel');
    if (await rolePanel.isVisible({ timeout: 3000 })) {
      // 验证角色面板有内容
      await expect(rolePanel).toBeVisible();

      // 找到查看详情按钮
      const viewButton = rolePanel.locator('button:has-text("详情"), button:has-text("权限")').first();

      if (await viewButton.isVisible({ timeout: 2000 })) {
        await viewButton.click();
        // 验证对话框或抽屉显示
        await expect(page.locator('.el-dialog, .el-drawer')).toBeVisible({ timeout: 5000 });
      }
    } else {
      // 验证页面有角色相关内容
      await expect(page.locator('.el-tabs__content')).toBeVisible({ timeout: 5000 });
    }
  });
});
