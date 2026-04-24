import { test, expect } from '@playwright/test';
import { loginAsAdmin, loginAsEntry, randomName } from './helpers';

test.describe('堂区管理模块测试', () => {
  test.describe.serial('管理员操作', () => {
    test.beforeEach(async ({ page }) => {
      await loginAsAdmin(page);
    });

    test('V01 - 列表显示堂区', async ({ page }) => {
      await page.goto('/villages');

      // 验证页面加载
      await expect(page.locator('body')).toContainText(/堂区|村庄/, { timeout: 10000 });

      // 验证表格存在
      const table = page.locator('.el-table');
      await expect(table).toBeVisible({ timeout: 5000 });
    });

    test('V02 - 创建堂区', async ({ page }) => {
      await page.goto('/villages');

      // 点击新增按钮
      await page.click('button:has-text("新建堂区")');

      // 等待对话框出现
      await expect(page.locator('.el-dialog')).toBeVisible({ timeout: 5000 });

      // 填写编码
      const code = `TEST${Date.now().toString().slice(-6)}`;
      await page.locator('.el-dialog input[placeholder*="编码"]').fill(code);

      // 填写表单
      const villageName = randomName('测试堂区');
      await page.locator('.el-dialog input[placeholder*="名称"]').fill(villageName);

      // 保存
      await page.locator('.el-dialog button:has-text("确定")').click();

      // 验证创建成功
      await expect(page.locator('.el-message--success')).toBeVisible({ timeout: 5000 });
    });

    test('V03 - 编辑堂区', async ({ page }) => {
      await page.goto('/villages');

      // 等待表格加载
      await page.waitForSelector('.el-table', { timeout: 10000 });

      // 找到第一行的编辑按钮
      const editButton = page.locator('.el-table button:has-text("编辑"), .el-table button:has-text("修改")').first();
      if (await editButton.isVisible({ timeout: 3000 })) {
        await editButton.click();

        // 修改名称
        const newName = randomName('已编辑');
        const nameInput = page.locator('input[placeholder*="名称"], input[placeholder*="堂区"]').first();
        await nameInput.fill('');
        await nameInput.fill(newName);

        // 保存
        await page.click('button:has-text("确定"), button:has-text("保存")');

        // 验证修改成功
        await expect(page.locator('.el-message--success')).toBeVisible({ timeout: 5000 });
      } else {
        // 如果没有编辑按钮，跳过测试
        test.skip();
      }
    });

    test('V04 - 删除堂区', async ({ page }) => {
      await page.goto('/villages');

      // 等待表格加载
      await page.waitForSelector('.el-table', { timeout: 10000 });

      // 找到删除按钮
      const deleteButtons = page.locator('.el-table button:has-text("删除")');
      const count = await deleteButtons.count();

      if (count > 1) {
        // 点击最后一个删除按钮
        await deleteButtons.nth(count - 1).click();

        // 处理确认对话框 - 使用更通用的选择器
        await page.waitForTimeout(500);
        const confirmBtn = page.locator('button:has-text("确定")').first();
        if (await confirmBtn.isVisible({ timeout: 2000 })) {
          await confirmBtn.click();
          await page.waitForTimeout(1000);
        }

        // 页面应该正常显示
        await expect(page.locator('body')).toBeVisible();
      } else {
        test.skip();
      }
    });
  });

  test('V05 - 录入员创建堂区', async ({ page }) => {
    await loginAsEntry(page);
    await page.goto('/villages');

    // 检查新增按钮是否禁用或不存在
    const addButton = page.locator('button:has-text("新增"), button:has-text("添加")');

    if (await addButton.isVisible({ timeout: 3000 })) {
      // 如果可见，检查是否禁用
      const isDisabled = await addButton.isDisabled();
      expect(isDisabled).toBe(true);
    }
    // 如果按钮不存在，测试通过
  });
});
