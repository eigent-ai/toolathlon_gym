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

import { EventEmitter } from 'events';
import * as playwright from 'playwright';
import { callOnPageNoTrace, waitForCompletion } from './tools/utils.js';
import { logUnhandledError } from './log.js';
import { ManualPromise } from './manualPromise.js';
import { ModalState } from './tools/tool.js';
import { outputFile } from './config.js';

import type { Context } from './context.js';

type PageEx = playwright.Page & {
  _snapshotForAI: () => Promise<string>;
};

export const TabEvents = {
  modalState: 'modalState'
};

export type TabEventsInterface = {
  [TabEvents.modalState]: [modalState: ModalState];
};

export class Tab extends EventEmitter<TabEventsInterface> {
  readonly context: Context;
  readonly page: playwright.Page;
  private _consoleMessages: ConsoleMessage[] = [];
  private _recentConsoleMessages: ConsoleMessage[] = [];
  private _requests: Map<playwright.Request, playwright.Response | null> = new Map();
  private _onPageClose: (tab: Tab) => void;
  private _modalStates: ModalState[] = [];
  private _downloads: { download: playwright.Download, finished: boolean, outputFile: string }[] = [];
  private _fullSnapshot: string = '';
  private _snapshotSpans: string[] = [];
  private _currentSpanIndex: number = 0;
  private _snapshotSpanSize: number = 2000;
  private _globalLines: string[] = [];
  private _spanToGlobalLineMap: Array<{ startLine: number; endLine: number }> = [];

  constructor(context: Context, page: playwright.Page, onPageClose: (tab: Tab) => void) {
    super();
    this.context = context;
    this.page = page;
    this._onPageClose = onPageClose;
    this._snapshotSpanSize = context.config.spanSize || 2000;
    page.on('console', event => this._handleConsoleMessage(messageToConsoleMessage(event)));
    page.on('pageerror', error => this._handleConsoleMessage(pageErrorToConsoleMessage(error)));
    page.on('request', request => this._requests.set(request, null));
    page.on('response', response => this._requests.set(response.request(), response));
    page.on('close', () => this._onClose());
    page.on('filechooser', chooser => {
      this.setModalState({
        type: 'fileChooser',
        description: 'File chooser',
        fileChooser: chooser,
      });
    });
    page.on('dialog', dialog => this._dialogShown(dialog));
    page.on('download', download => {
      void this._downloadStarted(download);
    });
    page.setDefaultNavigationTimeout(60000);
    page.setDefaultTimeout(5000);
  }

  modalStates(): ModalState[] {
    return this._modalStates;
  }

  setModalState(modalState: ModalState) {
    this._modalStates.push(modalState);
    this.emit(TabEvents.modalState, modalState);
  }

  clearModalState(modalState: ModalState) {
    this._modalStates = this._modalStates.filter(state => state !== modalState);
  }

  modalStatesMarkdown(): string[] {
    const result: string[] = ['### Modal state'];
    if (this._modalStates.length === 0)
      result.push('- There is no modal state present');
    for (const state of this._modalStates) {
      const tool = this.context.tools.filter(tool => 'clearsModalState' in tool).find(tool => tool.clearsModalState === state.type);
      result.push(`- [${state.description}]: can be handled by the "${tool?.schema.name}" tool`);
    }
    return result;
  }

  private _dialogShown(dialog: playwright.Dialog) {
    this.setModalState({
      type: 'dialog',
      description: `"${dialog.type()}" dialog with message "${dialog.message()}"`,
      dialog,
    });
  }

  private async _downloadStarted(download: playwright.Download) {
    const entry = {
      download,
      finished: false,
      outputFile: await outputFile(this.context.config, download.suggestedFilename())
    };
    this._downloads.push(entry);
    await download.saveAs(entry.outputFile);
    entry.finished = true;
  }

  private _clearCollectedArtifacts() {
    this._consoleMessages.length = 0;
    this._recentConsoleMessages.length = 0;
    this._requests.clear();
    this._resetSnapshot();
  }

  private _resetSnapshot() {
    this._fullSnapshot = '';
    this._snapshotSpans = [];
    this._currentSpanIndex = 0;
    this._globalLines = [];
    this._spanToGlobalLineMap = [];
  }

  private _splitSnapshotIntoSpans(snapshot: string): string[] {
    const lines = snapshot.split('\n');
    this._globalLines = lines; // Store global lines

    // If span size is -1, return the entire snapshot as a single span
    if (this._snapshotSpanSize === -1) {
      this._spanToGlobalLineMap = [{
        startLine: 1,
        endLine: lines.length
      }];
      return [snapshot];
    }

    const spans: string[] = [];
    this._spanToGlobalLineMap = []; // Reset span mapping

    let currentSpan = '';
    let currentLength = 0;
    let spanStartLineIndex = 0;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      let lineToAdd = line + '\n';

      // If the line itself is too long, truncate it
      if (lineToAdd.length > this._snapshotSpanSize) {
        const originalLength = line.length;
        const maxLineLength = this._snapshotSpanSize - 50; // Reserve space for truncation indicator
        lineToAdd = line.substring(0, maxLineLength) + `... [line truncated, originally with ${originalLength} chars]\n`;
      }

      // If adding this line would exceed the span size and we have content
      if (currentLength + lineToAdd.length > this._snapshotSpanSize && currentSpan.length > 0) {
        spans.push(currentSpan.trimEnd());
        // Record the line range for this span (1-based)
        this._spanToGlobalLineMap.push({
          startLine: spanStartLineIndex + 1,
          endLine: i
        });

        currentSpan = lineToAdd;
        currentLength = lineToAdd.length;
        spanStartLineIndex = i;
      } else {
        currentSpan += lineToAdd;
        currentLength += lineToAdd.length;
      }
    }

    // Add the last span if it has content
    if (currentSpan.trim().length > 0) {
      spans.push(currentSpan.trimEnd());
      this._spanToGlobalLineMap.push({
        startLine: spanStartLineIndex + 1,
        endLine: lines.length
      });
    }

    return spans.length > 0 ? spans : [''];
  }

  setSnapshotSpanSize(size: number) {
    this._snapshotSpanSize = size === -1 ? -1 : Math.max(100, size); // Allow -1 for complete snapshot, minimum 100 chars otherwise
    if (this._fullSnapshot) {
      this._snapshotSpans = this._splitSnapshotIntoSpans(this._fullSnapshot);
      this._currentSpanIndex = Math.min(this._currentSpanIndex, this._snapshotSpans.length - 1);
    }
  }

  getSnapshotSpanSize(): number {
    return this._snapshotSpanSize;
  }

  getCurrentSpanIndex(): number {
    return this._currentSpanIndex;
  }

  getTotalSpans(): number {
    return this._snapshotSpans.length;
  }

  navigateToSpan(index: number): { success: boolean; span: string; spanIndex: number; totalSpans: number } {
    if (this._snapshotSpans.length === 0)
      return { success: false, span: '', spanIndex: 0, totalSpans: 0 };


    const clampedIndex = Math.max(0, Math.min(index, this._snapshotSpans.length - 1));
    this._currentSpanIndex = clampedIndex;

    return {
      success: true,
      span: this._snapshotSpans[clampedIndex],
      spanIndex: clampedIndex,
      totalSpans: this._snapshotSpans.length
    };
  }

  navigateToFirstSpan() {
    return this.navigateToSpan(0);
  }

  navigateToLastSpan() {
    return this.navigateToSpan(this._snapshotSpans.length - 1);
  }

  navigateToNextSpan() {
    return this.navigateToSpan(this._currentSpanIndex + 1);
  }

  navigateToPrevSpan() {
    return this.navigateToSpan(this._currentSpanIndex - 1);
  }

  searchInSnapshot(pattern: string, flags?: string): { spanIndices: number[]; matches: Array<{ spanIndex: number; line: string; inSpanLineNumber: number; globalLineNumber: number }> } {
    const regex = new RegExp(pattern, flags || 'gi');
    const spanIndices: number[] = [];
    const matches: Array<{ spanIndex: number; line: string; inSpanLineNumber: number; globalLineNumber: number }> = [];

    this._snapshotSpans.forEach((span, spanIndex) => {
      const lines = span.split('\n');
      let hasMatch = false;
      const spanLineRange = this._spanToGlobalLineMap[spanIndex];

      lines.forEach((line, lineIndex) => {
        if (regex.test(line)) {
          hasMatch = true;
          const globalLineNumber = spanLineRange ? spanLineRange.startLine + lineIndex : lineIndex + 1;
          matches.push({
            spanIndex,
            line: line.trim(),
            inSpanLineNumber: lineIndex + 1,
            globalLineNumber
          });
        }
      });

      if (hasMatch)
        spanIndices.push(spanIndex);

    });

    return { spanIndices, matches };
  }

  navigateToLine(globalLineNumber: number, contextLines = 3): { success: boolean; content: string; lineInfo: string } {
    if (this._globalLines.length === 0)
      return { success: false, content: '', lineInfo: 'No snapshot available. Take a snapshot first.' };


    const targetLineIndex = globalLineNumber - 1; // Convert to 0-based
    if (targetLineIndex < 0 || targetLineIndex >= this._globalLines.length) {
      return {
        success: false,
        content: '',
        lineInfo: `Line ${globalLineNumber} is out of range. Snapshot has ${this._globalLines.length} lines.`
      };
    }

    // Calculate context range
    const startLine = Math.max(0, targetLineIndex - contextLines);
    const endLine = Math.min(this._globalLines.length - 1, targetLineIndex + contextLines);

    // Find which spans contain these lines
    const involvedSpans: number[] = [];
    for (let spanIndex = 0; spanIndex < this._spanToGlobalLineMap.length; spanIndex++) {
      const spanRange = this._spanToGlobalLineMap[spanIndex];
      // Check if this span overlaps with our context range (convert to 0-based for comparison)
      if (spanRange.startLine - 1 <= endLine && spanRange.endLine - 1 >= startLine)
        involvedSpans.push(spanIndex);

    }

    // Build the context content
    const contextContent: string[] = [];
    for (let i = startLine; i <= endLine; i++) {
      const lineNumber = i + 1;
      const isTarget = i === targetLineIndex;
      const marker = isTarget ? '>>> ' : '    ';
      contextContent.push(`${marker}${lineNumber}: ${this._globalLines[i]}`);
    }

    const spanInfo = involvedSpans.length > 0
      ? `Lines from spans: ${involvedSpans.map(s => s + 1).join(', ')}`
      : 'Span information unavailable';

    return {
      success: true,
      content: contextContent.join('\n'),
      lineInfo: `Showing lines ${startLine + 1}-${endLine + 1} (±${contextLines} context around line ${globalLineNumber})\n${spanInfo}`
    };
  }

  private _handleConsoleMessage(message: ConsoleMessage) {
    this._consoleMessages.push(message);
    this._recentConsoleMessages.push(message);
  }

  private _onClose() {
    this._clearCollectedArtifacts();
    this._onPageClose(this);
  }

  async title(): Promise<string> {
    return await callOnPageNoTrace(this.page, page => page.title());
  }

  async waitForLoadState(state: 'load', options?: { timeout?: number }): Promise<void> {
    await callOnPageNoTrace(this.page, page => page.waitForLoadState(state, options).catch(logUnhandledError));
  }

  async navigate(url: string) {
    this._clearCollectedArtifacts();

    const downloadEvent = callOnPageNoTrace(this.page, page => page.waitForEvent('download').catch(logUnhandledError));
    try {
      await this.page.goto(url, { waitUntil: 'domcontentloaded' });
    } catch (_e: unknown) {
      const e = _e as Error;
      const mightBeDownload =
        e.message.includes('net::ERR_ABORTED') // chromium
        || e.message.includes('Download is starting'); // firefox + webkit
      if (!mightBeDownload)
        throw e;
      // on chromium, the download event is fired *after* page.goto rejects, so we wait a lil bit
      const download = await Promise.race([
        downloadEvent,
        new Promise(resolve => setTimeout(resolve, 3000)),
      ]);
      if (!download)
        throw e;
      // Make sure other "download" listeners are notified first.
      await new Promise(resolve => setTimeout(resolve, 500));
      return;
    }

    // Cap load event to 5 seconds, the page is operational at this point.
    await this.waitForLoadState('load', { timeout: 5000 });
  }

  consoleMessages(): ConsoleMessage[] {
    return this._consoleMessages;
  }

  requests(): Map<playwright.Request, playwright.Response | null> {
    return this._requests;
  }

  private _takeRecentConsoleMarkdown(): string[] {
    if (!this._recentConsoleMessages.length)
      return [];
    const result = this._recentConsoleMessages.map(message => {
      return `- ${trim(message.toString(), 100)}`;
    });
    return [`### New console messages`, ...result, ''];
  }

  private _listDownloadsMarkdown(): string[] {
    if (!this._downloads.length)
      return [];

    const result: string[] = ['### Downloads'];
    for (const entry of this._downloads) {
      if (entry.finished)
        result.push(`- Downloaded file ${entry.download.suggestedFilename()} to ${entry.outputFile}`);
      else
        result.push(`- Downloading file ${entry.download.suggestedFilename()} ...`);
    }
    result.push('');
    return result;
  }

  async captureSnapshot(): Promise<string> {
    const result: string[] = [];
    if (this.modalStates().length) {
      result.push(...this.modalStatesMarkdown());
      return result.join('\n');
    }

    result.push(...this._takeRecentConsoleMarkdown());
    result.push(...this._listDownloadsMarkdown());

    await this._raceAgainstModalStates(async () => {
      // Get the full snapshot
      const fullSnapshot = await (this.page as PageEx)._snapshotForAI();

      // Smart span preservation logic
      if (this._fullSnapshot !== fullSnapshot) {
        const previousSpans = this._snapshotSpans;
        const previousCurrentSpanIndex = this._currentSpanIndex;

        // Update snapshot and create new spans
        this._fullSnapshot = fullSnapshot;
        this._snapshotSpans = this._splitSnapshotIntoSpans(fullSnapshot);

        // Determine if we should preserve current span position
        if (previousSpans.length === 0) {
          // First time snapshot - start at first span
          this._currentSpanIndex = 0;
        } else if (this._snapshotSpans.length === previousSpans.length &&
                   previousCurrentSpanIndex < this._snapshotSpans.length) {
          // Same number of spans - check if only current span changed
          let onlyCurrentSpanChanged = true;

          for (let i = 0; i < this._snapshotSpans.length; i++) {
            if (i !== previousCurrentSpanIndex && this._snapshotSpans[i] !== previousSpans[i]) {
              onlyCurrentSpanChanged = false;
              break;
            }
          }

          if (onlyCurrentSpanChanged) {
            // Only current span changed - stay in same position
            this._currentSpanIndex = previousCurrentSpanIndex;
          } else {
            // Multiple spans changed - reset to first span
            this._currentSpanIndex = 0;
          }
        } else {
          // Different number of spans - reset to first span
          this._currentSpanIndex = 0;
        }

        // Ensure current span index is within bounds
        this._currentSpanIndex = Math.min(this._currentSpanIndex, this._snapshotSpans.length - 1);
      }

      // Get current span
      const currentSpan = this._snapshotSpans[this._currentSpanIndex] || '';

      if (this._snapshotSpanSize === -1) {
        // Complete snapshot mode - no span information needed
        result.push(
            `### Page state`,
            `- Page URL: ${this.page.url()}`,
            `- Page Title: ${await this.page.title()}`,
            `- Page Snapshot:`,
            '```yaml',
            currentSpan,
            '```'
        );
      } else {
        // Span mode - show span information and navigation hints
        result.push(
            `### Page state`,
            `- Page URL: ${this.page.url()}`,
            `- Page Title: ${await this.page.title()}`,
            `- Page Snapshot (Span ${this._currentSpanIndex + 1} of ${this._snapshotSpans.length}):`,
            '```yaml',
            currentSpan,
            '```',
            '',
            `*Use snapshot navigation tools to view other spans. Current span size: ${this._snapshotSpanSize} characters*`
        );
      }
    });
    return result.join('\n');
  }

  private _javaScriptBlocked(): boolean {
    return this._modalStates.some(state => state.type === 'dialog');
  }

  private async _raceAgainstModalStates(action: () => Promise<void>): Promise<ModalState | undefined> {
    if (this.modalStates().length)
      return this.modalStates()[0];

    const promise = new ManualPromise<ModalState>();
    const listener = (modalState: ModalState) => promise.resolve(modalState);
    this.once(TabEvents.modalState, listener);

    return await Promise.race([
      action().then(() => {
        this.off(TabEvents.modalState, listener);
        return undefined;
      }),
      promise,
    ]);
  }

  async waitForCompletion(callback: () => Promise<void>) {
    await this._raceAgainstModalStates(() => waitForCompletion(this, callback));
  }

  async refLocator(params: { element: string, ref: string }): Promise<playwright.Locator> {
    return (await this.refLocators([params]))[0];
  }

  async refLocators(params: { element: string, ref: string }[]): Promise<playwright.Locator[]> {
    const snapshot = await (this.page as PageEx)._snapshotForAI();
    return params.map(param => {
      if (!snapshot.includes(`[ref=${param.ref}]`))
        throw new Error(`Ref ${param.ref} not found in the current page snapshot. Try capturing new snapshot.`);
      return this.page.locator(`aria-ref=${param.ref}`).describe(param.element);
    });
  }

  async waitForTimeout(time: number) {
    if (this._javaScriptBlocked()) {
      await new Promise(f => setTimeout(f, time));
      return;
    }

    await callOnPageNoTrace(this.page, page => {
      return page.evaluate(() => new Promise(f => setTimeout(f, 1000)));
    });
  }
}

export type ConsoleMessage = {
  type: ReturnType<playwright.ConsoleMessage['type']> | undefined;
  text: string;
  toString(): string;
};

function messageToConsoleMessage(message: playwright.ConsoleMessage): ConsoleMessage {
  return {
    type: message.type(),
    text: message.text(),
    toString: () => `[${message.type().toUpperCase()}] ${message.text()} @ ${message.location().url}:${message.location().lineNumber}`,
  };
}

function pageErrorToConsoleMessage(errorOrValue: Error | any): ConsoleMessage {
  if (errorOrValue instanceof Error) {
    return {
      type: undefined,
      text: errorOrValue.message,
      toString: () => errorOrValue.stack || errorOrValue.message,
    };
  }
  return {
    type: undefined,
    text: String(errorOrValue),
    toString: () => String(errorOrValue),
  };
}

function trim(text: string, maxLength: number) {
  if (text.length <= maxLength)
    return text;
  return text.slice(0, maxLength) + '...';
}
