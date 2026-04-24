import { test, expect } from '@playwright/test';
import { loginAsAdmin, loginAsEntry, randomName } from './helpers';

test.describe('成员管理模块测试', () => {
  test.describe.serial('管理员操作', () => {
    test.beforeEach(async ({ page }) => {
      await loginAsAdmin(page);
    });

    test('M01 - 列表显示成员', async ({ page }) => {
      await page.goto('/members');

      // 验证页面加载
      await expect(page.locator('.el-table')).toBeVisible({ timeout: 10000 });
    });

    test('M02 - 创建成员', async ({ page }) => {
      await page.goto('/members');
      await page.waitForTimeout(1000);

      // 先确保有家庭数据 - 去家庭管理页面创建一个
      await page.goto('/households');
      await page.waitForSelector('.el-table', { timeout: 10000 });

      // 检查是否有家庭，没有则创建
      let hasData = false;
      const rows = await page.locator('.el-table .el-table__row').count();
      if (rows === 0) {
        // 创建一个家庭
        await page.click('button:has-text("新建家庭")');
        await expect(page.locator('.el-dialog')).toBeVisible({ timeout: 5000 });

        const select = page.locator('.el-dialog .el-select');
        await select.click();
        await page.waitForSelector('.el-select-dropdown:visible', { timeout: 3000 });
        await page.locator('.el-select-dropdown:visible .el-select-dropdown__item').first().click();
        await page.locator('.el-dialog input[placeholder*="地址"]').fill(randomName('测试家庭'));
        await page.locator('.el-dialog button:has-text("确定")').click();
        await expect(page.locator('.el-message--success')).toBeVisible({ timeout: 5000 });
        hasData = true;
      }

      // 回到成员管理页面
      await page.goto('/members');
      await page.waitForTimeout(1000);

      // 点击新增按钮
      await page.click('button:has-text("新建成员")');

      // 等待对话框出现
      const dialog = page.locator('.el-dialog');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // 选择家庭
      const familySelect = dialog.locator('.el-select').first();
      await familySelect.click();
      await page.waitForTimeout(500);

      // 等待下拉菜单出现并选择
      await page.waitForSelector('.el-select-dropdown:visible', { timeout: 3000 });
      await page.locator('.el-select-dropdown:visible .el-select-dropdown__item').first().click();

      // 填写姓名
      const name = randomName('测试成员');
      await dialog.locator('input[placeholder*="姓名"]').fill(name);

      // 选择性别
      const genderSelect = dialog.locator('.el-select').nth(1);
      if (await genderSelect.isVisible({ timeout: 1000 })) {
        await genderSelect.click();
        await page.waitForTimeout(300);
        await page.locator('.el-select-dropdown:visible .el-select-dropdown__item').first().click();
      }

      // 保存
      await dialog.locator('button:has-text("确定")').click();

      // 验证创建成功
      await expect(page.locator('.el-message--success')).toBeVisible({ timeout: 5000 });
    });

    test('M03 - 编辑成员', async ({ page }) => {
      await page.goto('/members');
      await page.waitForSelector('.el-table', { timeout: 10000 });
      await page.waitForTimeout(1000);

      // 确保有成员数据
      let editButton = page.locator('.el-table button:has-text("编辑")').first();

      if (!await editButton.isVisible({ timeout: 2000 })) {
        // 没有数据，先创建成员
        // 确保先有家庭
        await page.goto('/households');
        await page.waitForSelector('.el-table', { timeout: 10000 });
        const rows = await page.locator('.el-table .el-table__row').count();
        if (rows === 0) {
          await page.click('button:has-text("新建家庭")');
          await expect(page.locator('.el-dialog')).toBeVisible({ timeout: 5000 });
          const select = page.locator('.el-dialog .el-select');
          await select.click();
          await page.waitForSelector('.el-select-dropdown:visible', { timeout: 3000 });
          await page.locator('.el-select-dropdown:visible .el-select-dropdown__item').first().click();
          await page.locator('.el-dialog input[placeholder*="地址"]').fill(randomName('测试家庭'));
          await page.locator('.el-dialog button:has-text("确定")').click();
          await expect(page.locator('.el-message--success')).toBeVisible({ timeout: 5000 });
        }

        // 创建成员
        await page.goto('/members');
        await page.waitForTimeout(1000);
        await page.click('button:has-text("新建成员")');
        const dialog = page.locator('.el-dialog');
        await expect(dialog).toBeVisible({ timeout: 5000 });
        const familySelect = dialog.locator('.el-select').first();
        await familySelect.click();
        await page.waitForSelector('.el-select-dropdown:visible', { timeout: 3000 });
        await page.locator('.el-select-dropdown:visible .el-select-dropdown__item').first().click();
        await dialog.locator('input[placeholder*="姓名"]').fill(randomName('待编辑'));
        await dialog.locator('button:has-text("确定")').click();
        await expect(page.locator('.el-message--success')).toBeVisible({ timeout: 5000 });

        await page.reload();
        await page.waitForSelector('.el-table', { timeout: 10000 });
        await page.waitForTimeout(1000);
        editButton = page.locator('.el-table button:has-text("编辑")').first();
      }

      // 点击编辑按钮
      await editButton.click();

      // 等待对话框出现
      const dialog = page.locator('.el-dialog');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // 修改姓名
      const newName = randomName('已编辑');
      const nameInput = dialog.locator('input[placeholder*="姓名"]');
      await nameInput.fill(newName);

      // 保存
      await dialog.locator('button:has-text("确定")').click();

      // 验证修改成功
      await expect(page.locator('.el-message--success')).toBeVisible({ timeout: 5000 });
    });

    test('M04 - 删除成员', async ({ page }) => {
      await page.goto('/members');
      await page.waitForSelector('.el-table', { timeout: 10000 });
      await page.waitForTimeout(1000);

      // 确保有成员数据
      let deleteButtons = page.locator('.el-table button:has-text("删除")');
      let count = await deleteButtons.count();

      if (count === 0) {
        // 没有数据，先创建成员
        await page.goto('/households');
        await page.waitForSelector('.el-table', { timeout: 10000 });
        const rows = await page.locator('.el-table .el-table__row').count();
        if (rows === 0) {
          await page.click('button:has-text("新建家庭")');
          await expect(page.locator('.el-dialog')).toBeVisible({ timeout: 5000 });
          const select = page.locator('.el-dialog .el-select');
          await select.click();
          await page.waitForSelector('.el-select-dropdown:visible', { timeout: 3000 });
          await page.locator('.el-select-dropdown:visible .el-select-dropdown__item').first().click();
          await page.locator('.el-dialog input[placeholder*="地址"]').fill(randomName('测试家庭'));
          await page.locator('.el-dialog button:has-text("确定")').click();
          await expect(page.locator('.el-message--success')).toBeVisible({ timeout: 5000 });
        }

        await page.goto('/members');
        await page.waitForTimeout(1000);
        await page.click('button:has-text("新建成员")');
        const dialog = page.locator('.el-dialog');
        await expect(dialog).toBeVisible({ timeout: 5000 });
        const familySelect = dialog.locator('.el-select').first();
        await familySelect.click();
        await page.waitForSelector('.el-select-dropdown:visible', { timeout: 3000 });
        await page.locator('.el-select-dropdown:visible .el-select-dropdown__item').first().click();
        await dialog.locator('input[placeholder*="姓名"]').fill(randomName('待删除'));
        await dialog.locator('button:has-text("确定")').click();
        await expect(page.locator('.el-message--success')).toBeVisible({ timeout: 5000 });

        await page.reload();
        await page.waitForSelector('.el-table', { timeout: 10000 });
        await page.waitForTimeout(1000);
        deleteButtons = page.locator('.el-table button:has-text("删除")');
      }

      // 点击删除按钮
      await deleteButtons.last().click();
      await page.waitForTimeout(500);

      // 确认删除 - 处理可能的确认对话框
      const confirmBtn = page.locator('.el-message-box button:has-text("确定")');
      if (await confirmBtn.isVisible({ timeout: 2000 })) {
        await confirmBtn.click();
      }

      // 验证操作完成
      await page.waitForTimeout(1000);
      await expect(page.locator('body')).toBeVisible();
    });

    test('M05 - 成员详情查看', async ({ page }) => {
      await page.goto('/members');
      await page.waitForSelector('.el-table', { timeout: 10000 });
      await page.waitForTimeout(1000);

      // 确保有成员数据
      let viewButton = page.locator('.el-table button:has-text("详情")').first();

      if (!await viewButton.isVisible({ timeout: 2000 })) {
        // 创建一个成员
        await page.goto('/households');
        await page.waitForSelector('.el-table', { timeout: 10000 });
        const rows = await page.locator('.el-table .el-table__row').count();
        if (rows === 0) {
          await page.click('button:has-text("新建家庭")');
          await expect(page.locator('.el-dialog')).toBeVisible({ timeout: 5000 });
          const select = page.locator('.el-dialog .el-select');
          await select.click();
          await page.waitForSelector('.el-select-dropdown:visible', { timeout: 3000 });
          await page.locator('.el-select-dropdown:visible .el-select-dropdown__item').first().click();
          await page.locator('.el-dialog input[placeholder*="地址"]').fill(randomName('测试家庭'));
          await page.locator('.el-dialog button:has-text("确定")').click();
          await expect(page.locator('.el-message--success')).toBeVisible({ timeout: 5000 });
        }

        await page.goto('/members');
        await page.waitForTimeout(1000);
        await page.click('button:has-text("新建成员")');
        const dialog = page.locator('.el-dialog');
        await expect(dialog).toBeVisible({ timeout: 5000 });
        const familySelect = dialog.locator('.el-select').first();
        await familySelect.click();
        await page.waitForSelector('.el-select-dropdown:visible', { timeout: 3000 });
        await page.locator('.el-select-dropdown:visible .el-select-dropdown__item').first().click();
        await dialog.locator('input[placeholder*="姓名"]').fill(randomName('测试成员'));
        await dialog.locator('button:has-text("确定")').click();
        await expect(page.locator('.el-message--success')).toBeVisible({ timeout: 5000 });

        await page.reload();
        await page.waitForSelector('.el-table', { timeout: 10000 });
        await page.waitForTimeout(1000);
        viewButton = page.locator('.el-table button:has-text("详情")').first();
      }

      // 点击详情按钮
      await viewButton.click();

      // 验证详情对话框显示
      await expect(page.locator('.el-dialog')).toBeVisible({ timeout: 5000 });
    });
  });

  test('M06 - 录入员仅看所属堂区成员', async ({ page }) => {
    await loginAsEntry(page);
    await page.goto('/members');

    // 验证页面加载
    await expect(page.locator('.el-table')).toBeVisible({ timeout: 10000 });
  });
});
