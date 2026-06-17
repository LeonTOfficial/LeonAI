const { test, expect } = require('@playwright/test');

async function loginOrSetup(page) {
  await page.goto('/login');
  const setupForm = page.locator('form[action="/setup"]');
  if (await setupForm.isVisible().catch(() => false)) {
    await page.locator('#first_name').fill('Leon');
    await page.locator('#password').fill('playwright-pass');
    await page.locator('#password_confirm').fill('playwright-pass');
    await page.getByRole('button', { name: 'Setup abschließen' }).click();
  } else {
    await page.locator('#password').fill('playwright-pass');
    await page.getByRole('button', { name: 'Einloggen' }).click();
  }
  await expect(page).toHaveURL(/\/$/);
  await expect(page.locator('body')).toContainText('LEON AI');
}

async function installRichFixtures(page) {
  await page.evaluate(() => {
    window.DOMPurify = { sanitize: (html) => html };
    window.marked = {
      setOptions() {},
      parse(text) {
        return String(text)
          .replace(/```([A-Za-z0-9_+#.-]*)\n([\s\S]*?)```/g, (_match, lang, code) =>
            `<pre><code class="language-${lang || 'txt'}">${code
              .replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')}</code></pre>`)
          .replace(/\n/g, '<br>');
      },
    };
    window.Chart = function Chart(canvas) {
      canvas.dataset.chartRendered = 'true';
      this.destroy = () => {};
    };
    window.mermaid = {
      initialize() {},
      run({ nodes }) {
        nodes.forEach((node) => {
          const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
          svg.setAttribute('data-testid', 'mermaid-svg');
          node.replaceChildren(svg);
        });
        return Promise.resolve();
      },
    };
  });
}

test('login or first setup opens the chat shell', async ({ page }) => {
  await loginOrSetup(page);

  await expect(page.getByText('LEON AI').first()).toBeVisible();
  await expect(page.locator('#user-input')).toBeVisible();
  await expect(page.getByRole('link', { name: /Dashboard/i })).toBeVisible();
  await expect(page.locator('#status-dot')).toBeVisible();
});

test('dashboard loads without browser JavaScript errors', async ({ page }) => {
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await loginOrSetup(page);
  await page.addInitScript(() => {
    window.Chart = window.Chart || function Chart() {
      this.destroy = () => {};
      this.update = () => {};
    };
  });
  await page.goto('/dashboard');

  await expect(page.getByText('Dashboard.')).toBeVisible();
  await expect(page.getByText('Tokens')).toBeVisible();
  await expect(page.getByText('Privacy')).toBeVisible();
  expect(errors).toEqual([]);
});

test('chat renders color tags, Chart.js canvas, and Mermaid SVG from fixtures', async ({ page }) => {
  await loginOrSetup(page);
  await installRichFixtures(page);

  await page.evaluate(() => {
    Leon.state.currentRoomId = 999;
    Leon.state.activeLeafId = 1;
    Leon.state.messages = [{
      id: 1,
      role: 'ai',
      parent_id: null,
      created: new Date().toISOString(),
      content: `Eine [rot]wichtige[/rot] Markierung.\n\n\`\`\`chart\n{"type":"bar","data":{"labels":["A","B"],"datasets":[{"label":"Werte","data":[2,4]}]}}\n\`\`\`\n\n\`\`\`mermaid\nflowchart TD\nA[Start] --> B[Ende]\n\`\`\``,
    }];
    Leon.renderMessages();
  });

  await expect(page.locator('.leon-color-red', { hasText: 'wichtige' })).toBeVisible();
  await expect(page.locator('.rich-chart-body canvas[data-chart-rendered="true"]')).toBeVisible();
  await expect(page.locator('[data-testid="mermaid-svg"]')).toBeVisible();
});

test('artifact preview renders simple HTML visibly inside the iframe', async ({ page }) => {
  await loginOrSetup(page);
  await installRichFixtures(page);

  await page.evaluate(() => {
    Leon.state.currentRoomId = 1000;
    Leon.state.activeLeafId = 2;
    Leon.state.messages = [{
      id: 2,
      role: 'ai',
      parent_id: null,
      created: new Date().toISOString(),
      content: '```html\n<!doctype html><html><body><h1 id="qa-preview">Preview OK</h1></body></html>\n```',
    }];
    Leon.renderMessages();
  });

  await expect(page.locator('#artifact-panel')).toHaveClass(/show/);
  await expect(page.frameLocator('#artifact-frame').locator('#qa-preview')).toHaveText('Preview OK');
});
