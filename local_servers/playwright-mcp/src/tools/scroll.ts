/**
 * Copyright (c) Microsoft Corporation.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { z } from 'zod';
import { defineTabTool } from './tool.js';

const scrollUp = defineTabTool({
  capability: 'core',
  schema: {
    name: 'browser_scroll_up',
    title: 'Scroll up',
    description: 'Scroll the page up to see content above the current viewport',
    inputSchema: z.object({
      amount: z.number().optional().describe('Amount to scroll in pixels. Defaults to one viewport height.'),
    }),
    type: 'readOnly',
  },

  handle: async (tab, params, response) => {
    const viewportHeight = tab.page.viewportSize()?.height || 800;
    const scrollAmount = params.amount || viewportHeight;

    response.setIncludeSnapshot();
    response.addCode(`// Scroll up by ${scrollAmount}px`);
    response.addCode(`await page.evaluate(() => window.scrollBy(0, -${scrollAmount}));`);

    await tab.waitForCompletion(async () => {
      await tab.page.evaluate(amount => {
        window.scrollBy(0, -amount);
      }, scrollAmount);
    });
  },
});

const scrollDown = defineTabTool({
  capability: 'core',
  schema: {
    name: 'browser_scroll_down',
    title: 'Scroll down',
    description: 'Scroll the page down to see content below the current viewport',
    inputSchema: z.object({
      amount: z.number().optional().describe('Amount to scroll in pixels. Defaults to one viewport height.'),
    }),
    type: 'readOnly',
  },

  handle: async (tab, params, response) => {
    const viewportHeight = tab.page.viewportSize()?.height || 800;
    const scrollAmount = params.amount || viewportHeight;

    response.setIncludeSnapshot();
    response.addCode(`// Scroll down by ${scrollAmount}px`);
    response.addCode(`await page.evaluate(() => window.scrollBy(0, ${scrollAmount}));`);

    await tab.waitForCompletion(async () => {
      await tab.page.evaluate(amount => {
        window.scrollBy(0, amount);
      }, scrollAmount);
    });
  },
});

const scrollToTop = defineTabTool({
  capability: 'core',
  schema: {
    name: 'browser_scroll_to_top',
    title: 'Scroll to top',
    description: 'Scroll to the top of the page',
    inputSchema: z.object({}),
    type: 'readOnly',
  },

  handle: async (tab, params, response) => {
    response.setIncludeSnapshot();
    response.addCode(`// Scroll to top of page`);
    response.addCode(`await page.evaluate(() => window.scrollTo(0, 0));`);

    await tab.waitForCompletion(async () => {
      await tab.page.evaluate(() => {
        window.scrollTo(0, 0);
      });
    });
  },
});

const scrollToBottom = defineTabTool({
  capability: 'core',
  schema: {
    name: 'browser_scroll_to_bottom',
    title: 'Scroll to bottom',
    description: 'Scroll to the bottom of the page',
    inputSchema: z.object({}),
    type: 'readOnly',
  },

  handle: async (tab, params, response) => {
    response.setIncludeSnapshot();
    response.addCode(`// Scroll to bottom of page`);
    response.addCode(`await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));`);

    await tab.waitForCompletion(async () => {
      await tab.page.evaluate(() => {
        window.scrollTo(0, document.body.scrollHeight);
      });
    });
  },
});

export default [
  scrollUp,
  scrollDown,
  scrollToTop,
  scrollToBottom,
];
