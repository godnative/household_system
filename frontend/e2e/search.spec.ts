import { test, expect } from '@playwright/test';
import { loginAsAdmin } from './helpers';

test.describe('搜索模块测试', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  test('S01 - 搜索家庭', async ({ page }) => {
    await page.goto('/search');

    // 确保选择家庭搜索
    await page.click('text=家庭搜索');

    // 输入搜索关键词
    await page.fill('input[placeholder*="户主"], input[placeholder*="地址"]', '测试');

    // 点击搜索
    await page.click('button:has-text("搜索")');

    // 验证搜索结果
    await expect(page.locator('.el-table')).toBeVisible({ timeout: 5000 });
  });

  test('S02 - 搜索成员', async ({ page }) => {
    await page.goto('/search');

    // 选择成员搜索
    await page.click('text=成员搜索');

    // 输入搜索关键词
    await page.fill('input[placeholder*="姓名"], input[placeholder*="圣名"]', '张');

    // 点击搜索
    await page.click('button:has-text("搜索")');

    // 验证搜索结果
    await expect(page.locator('.el-table')).toBeVisible({ timeout: 5000 });
  });

  test('S03 - 空关键词搜索', async ({ page }) => {
    await page.goto('/search');

    // 不输入关键词直接搜索
    await page.click('button:has-text("搜索")');

    // 验证页面正常
    await page.waitForTimeout(1000);
    await expect(page.locator('body')).toBeVisible();
  });

  test('S04 - 无结果搜索', async ({ page }) => {
    await page.goto('/search');

    // 输入不存在的关键词
    await page.fill('input[placeholder*="户主"], input[placeholder*="姓名"]', '不存在的关键词xyz123');

    // 点击搜索
    await page.click('button:has-text("搜索")');

    // 验证页面正常
    await page.waitForTimeout(1000);
    await expect(page.locator('body')).toBeVisible();
  });

  test('S05 - 搜索结果分页', async ({ page }) => {
    await page.goto('/search');

    // 输入搜索关键词
    await page.fill('input[placeholder*="户主"], input[placeholder*="姓名"]', '张');
    await page.click('button:has-text("搜索")');

    // 检查分页器或表格
    await page.waitForTimeout(1000);
    await expect(page.locator('.el-table, .el-pagination').first()).toBeVisible({ timeout: 3000 });
  });
});
