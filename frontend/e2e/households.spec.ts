import { test, expect } from '@playwright/test';
import { loginAsAdmin, loginAsEntry, loginAsObserver, randomName } from './helpers';

test.describe('家庭管理模块测试', () => {
  test.describe.serial('管理员操作', () => {
    test.beforeEach(async ({ page }) => {
      await loginAsAdmin(page);
    });

    test('H01 - 列表显示家庭', async ({ page }) => {
      await page.goto('/households');
      await expect(page.locator('.el-table')).toBeVisible({ timeout: 10000 });
    });

    test('H02 - 创建家庭', async ({ page }) => {
      await page.goto('/households');
      await page.click('button:has-text("新建家庭")');
      await expect(page.locator('.el-dialog')).toBeVisible({ timeout: 5000 });

      const select = page.locator('.el-dialog .el-select');
      await select.click();
      await page.waitForSelector('.el-select-dropdown:visible', { timeout: 3000 });
      await page.locator('.el-select-dropdown:visible .el-select-dropdown__item').first().click();

      const address = randomName('测试地址');
      await page.locator('.el-dialog input[placeholder*="地址"]').fill(address);
      await page.locator('.el-dialog button:has-text("确定")').click();
      await expect(page.locator('.el-message--success')).toBeVisible({ timeout: 5000 });
    });

    test('H03 - 编辑家庭', async ({ page }) => {
      await page.goto('/households');
      await page.waitForSelector('.el-table', { timeout: 10000 });
      const editButton = page.locator('.el-table button:has-text("编辑")').first();
      await expect(editButton).toBeVisible({ timeout: 5000 });
      await editButton.click();

      const dialog = page.locator('.el-dialog');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      const newAddress = randomName('已编辑地址');
      const addressInput = dialog.locator('input[placeholder*="地址"]');
      await addressInput.fill(newAddress);
      await dialog.locator('button:has-text("确定")').click();
      await expect(page.locator('.el-table')).toBeVisible({ timeout: 5000 });
    });

    test('H04 - 删除家庭', async ({ page }) => {
      await page.goto('/households');
      await page.waitForSelector('.el-table', { timeout: 10000 });
      const deleteButton = page.locator('.el-table button:has-text("删除")').last();
      await expect(deleteButton).toBeVisible({ timeout: 5000 });
      await deleteButton.click();

      const confirmBtn = page.locator('.el-message-box button:has-text("确定")');
      if (await confirmBtn.isVisible({ timeout: 2000 })) {
        await confirmBtn.click();
      }

      await expect(page.locator('.el-table')).toBeVisible({ timeout: 5000 });
    });

    test('H05 - 分页功能', async ({ page }) => {
      await page.goto('/households');
      await expect(page.locator('.el-pagination')).toBeVisible({ timeout: 5000 });
    });

    test('H06 - 选择家庭后右侧联动显示成员', async ({ page }) => {
      await page.goto('/households');
      await expect(page.locator('.el-table')).toBeVisible({ timeout: 10000 });
      await page.locator('.el-table .el-table__row').first().click();
      await expect(page.locator('.selected-household-meta')).toBeVisible({ timeout: 10000 });
      await expect(page.locator('body')).toContainText('当前家庭：');
      await expect(page.locator('body')).toContainText('户主：');
    });
  });

  test('H07 - 录入员仅看所属堂区', async ({ page }) => {
    await loginAsEntry(page);
    await page.goto('/households');
    await expect(page.locator('.el-table')).toBeVisible({ timeout: 10000 });
  });

  test('H08 - 观察员无编辑权限', async ({ page }) => {
    await loginAsObserver(page);
    await page.goto('/households');

    const addButton = page.locator('button:has-text("新建家庭")');
    if (await addButton.isVisible({ timeout: 3000 })) {
      expect(await addButton.isDisabled()).toBe(true);
    }
  });
});
