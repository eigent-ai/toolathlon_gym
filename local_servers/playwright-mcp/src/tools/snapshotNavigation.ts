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

const snapshotNavigateToSpan = defineTabTool({
  capability: 'core',
  schema: {
    name: 'browser_snapshot_navigate_to_span',
    title: 'Navigate to specific snapshot span',
    description: 'Navigate to a specific span in the current page snapshot by index. Each span contains a portion of the page content (limited by span size). Use this when you know the exact span number you want to view, typically after using browser_snapshot_search to locate content.',
    inputSchema: z.object({
      spanIndex: z.number().int().min(0).describe('The span index to navigate to (0-based)'),
    }),
    type: 'readOnly',
  },

  handle: async (tab, params, response) => {
    const result = tab.navigateToSpan(params.spanIndex);

    if (result.success) {
      response.addResult(`Navigated to span ${result.spanIndex + 1} of ${result.totalSpans}`);
      response.addResult('```yaml\n' + result.span + '\n```');
    } else {
      response.addResult('No snapshot available. Take a snapshot first.');
    }
  },
});

const snapshotNavigateToFirstSpan = defineTabTool({
  capability: 'core',
  schema: {
    name: 'browser_snapshot_navigate_to_first_span',
    title: 'Navigate to first snapshot span',
    description: 'Navigate to the first span of the current page snapshot. This shows the beginning of the page content and is useful for starting from the top of the page when exploring content sequentially.',
    inputSchema: z.object({}),
    type: 'readOnly',
  },

  handle: async (tab, params, response) => {
    const result = tab.navigateToFirstSpan();

    if (result.success) {
      response.addResult(`Navigated to first span (1 of ${result.totalSpans})`);
      response.addResult('```yaml\n' + result.span + '\n```');
    } else {
      response.addResult('No snapshot available. Take a snapshot first.');
    }
  },
});

const snapshotNavigateToLastSpan = defineTabTool({
  capability: 'core',
  schema: {
    name: 'browser_snapshot_navigate_to_last_span',
    title: 'Navigate to last snapshot span',
    description: 'Navigate to the last span of the current page snapshot. This shows the end of the page content and is useful for accessing footer content, final form elements, or bottom navigation.',
    inputSchema: z.object({}),
    type: 'readOnly',
  },

  handle: async (tab, params, response) => {
    const result = tab.navigateToLastSpan();

    if (result.success) {
      response.addResult(`Navigated to last span (${result.spanIndex + 1} of ${result.totalSpans})`);
      response.addResult('```yaml\n' + result.span + '\n```');
    } else {
      response.addResult('No snapshot available. Take a snapshot first.');
    }
  },
});

const snapshotNavigateToNextSpan = defineTabTool({
  capability: 'core',
  schema: {
    name: 'browser_snapshot_navigate_to_next_span',
    title: 'Navigate to next snapshot span',
    description: 'Navigate to the next span in the current page snapshot. If already at the last span, stays at the last span. Use this for sequential exploration of page content from top to bottom.',
    inputSchema: z.object({}),
    type: 'readOnly',
  },

  handle: async (tab, params, response) => {
    const result = tab.navigateToNextSpan();

    if (result.success) {
      response.addResult(`Navigated to span ${result.spanIndex + 1} of ${result.totalSpans}`);
      response.addResult('```yaml\n' + result.span + '\n```');
    } else {
      response.addResult('No snapshot available. Take a snapshot first.');
    }
  },
});

const snapshotNavigateToPrevSpan = defineTabTool({
  capability: 'core',
  schema: {
    name: 'browser_snapshot_navigate_to_prev_span',
    title: 'Navigate to previous snapshot span',
    description: 'Navigate to the previous span in the current page snapshot. If already at the first span, stays at the first span. Use this for sequential exploration of page content from bottom to top.',
    inputSchema: z.object({}),
    type: 'readOnly',
  },

  handle: async (tab, params, response) => {
    const result = tab.navigateToPrevSpan();

    if (result.success) {
      response.addResult(`Navigated to span ${result.spanIndex + 1} of ${result.totalSpans}`);
      response.addResult('```yaml\n' + result.span + '\n```');
    } else {
      response.addResult('No snapshot available. Take a snapshot first.');
    }
  },
});

const snapshotSearch = defineTabTool({
  capability: 'core',
  schema: {
    name: 'browser_snapshot_search',
    title: 'Search in current snapshot',
    description: 'Search for a pattern across all spans of the current page snapshot using regular expressions. Returns matches with both global line numbers (across entire snapshot) and in-span line numbers (within each span). Shows which spans contain matches for navigation. Supports regex flags like "gi" for global case-insensitive search.',
    inputSchema: z.object({
      pattern: z.string().describe('The regex pattern to search for'),
      flags: z.string().optional().describe('Optional regex flags (e.g., "gi" for global case-insensitive)'),
    }),
    type: 'readOnly',
  },

  handle: async (tab, params, response) => {
    try {
      const searchResult = tab.searchInSnapshot(params.pattern, params.flags);

      if (searchResult.spanIndices.length === 0) {
        response.addResult(`No matches found for pattern: ${params.pattern}`);
        return;
      }

      response.addResult(`Found ${searchResult.matches.length} matches in ${searchResult.spanIndices.length} spans:`);
      response.addResult(`Spans with matches: ${searchResult.spanIndices.map(i => i + 1).join(', ')}`);

      // Show first few matches
      const maxMatches = 10;
      const matchesToShow = searchResult.matches.slice(0, maxMatches);

      for (const match of matchesToShow) {
        response.addResult(`\n**Span ${match.spanIndex + 1}, Global Line ${match.globalLineNumber}, In-Span Line ${match.inSpanLineNumber}:**`);
        response.addResult(`${match.line}`);
      }

      if (searchResult.matches.length > maxMatches)
        response.addResult(`\n... and ${searchResult.matches.length - maxMatches} more matches`);


      response.addResult(`\nUse navigation tools to view specific spans with matches.`);
    } catch (error) {
      response.addResult(`Error searching: ${error instanceof Error ? error.message : String(error)}`);
    }
  },
});

const snapshotNavigateToLine = defineTabTool({
  capability: 'core',
  schema: {
    name: 'browser_snapshot_navigate_to_line',
    title: 'Navigate to specific line in snapshot',
    description: 'Navigate to a specific global line number in the current page snapshot with configurable surrounding context lines. Shows which spans contain the context lines. The target line is marked with ">>>". Use this to quickly jump to specific content found via search results.',
    inputSchema: z.object({
      globalLineNumber: z.number().int().min(1).describe('The global line number to navigate to (1-based)'),
      contextLines: z.number().int().min(0).max(10).optional().describe('Number of context lines to show before and after the target line (default: 3)'),
    }),
    type: 'readOnly',
  },

  handle: async (tab, params, response) => {
    const result = tab.navigateToLine(params.globalLineNumber, params.contextLines);

    if (result.success) {
      response.addResult(result.lineInfo);
      response.addResult('```yaml\n' + result.content + '\n```');
    } else {
      response.addResult(result.lineInfo);
    }
  },
});

export default [
  snapshotNavigateToSpan,
  snapshotNavigateToFirstSpan,
  snapshotNavigateToLastSpan,
  snapshotNavigateToNextSpan,
  snapshotNavigateToPrevSpan,
  snapshotNavigateToLine,
  snapshotSearch,
];
