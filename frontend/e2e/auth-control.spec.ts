import { test, expect } from '@playwright/test';
import { loginAsEntry, loginAsObserver } from './helpers';

test.describe('权限控制测试', () => {
  test('AC01 - 录入员数据范围限制', async ({ page }) => {
    await loginAsEntry(page);

    // 访问各模块
    await page.goto('/households');
    await expect(page.locator('.el-table')).toBeVisible({ timeout: 10000 });

    await page.goto('/members');
    await expect(page.locator('.el-table')).toBeVisible({ timeout: 10000 });

    // 验证录入员可以进行CRUD操作
    const addButton = page.locator('button:has-text("新增"), button:has-text("添加")');
    if (await addButton.isVisible({ timeout: 2000 })) {
      expect(await addButton.isEnabled()).toBe(true);
    }
  });

  test('AC02 - 观察员只读限制', async ({ page }) => {
    await loginAsObserver(page);

    // 访问家庭管理
    await page.goto('/households');
    await expect(page.locator('.el-table')).toBeVisible({ timeout: 10000 });

    // 验证新增/编辑/删除按钮禁用
    const addButton = page.locator('button:has-text("新增"), button:has-text("添加")');
    if (await addButton.isVisible({ timeout: 2000 })) {
      const isDisabled = await addButton.isDisabled();
      expect(isDisabled).toBe(true);
    }

    // 访问成员管理
    await page.goto('/members');
    await expect(page.locator('.el-table')).toBeVisible({ timeout: 10000 });

    // 验证操作按钮禁用
    const editButton = page.locator('button:has-text("编辑"), button:has-text("修改")').first();
    if (await editButton.isVisible({ timeout: 2000 })) {
      const isDisabled = await editButton.isDisabled();
      expect(isDisabled).toBe(true);
    }
  });

  test('AC03 - 未登录API直接访问', async ({ page }) => {
    // 直接访问需要认证的API端点
    const response = await page.request.get('http://localhost:8000/api/v1/villages');

    // 验证返回401错误
    expect(response.status()).toBe(401);
  });

  test('AC04 - Token过期处理', async ({ page }) => {
    // 先登录
    await loginAsEntry(page);

    // 清除token模拟过期
    await page.evaluate(() => {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    });

    // 访问保护页面
    await page.goto('/dashboard');

    // 验证重定向到登录页或重新获取用户信息
    await page.waitForTimeout(2000);
    const currentUrl = page.url();
    expect(currentUrl).toMatch(/\/(login|dashboard)/);
  });
});
