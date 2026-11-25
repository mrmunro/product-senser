import { forwardRef, useCallback, useImperativeHandle, useRef, useState } from 'react';
import { Excalidraw, exportToBlob, serializeAsJSON } from '@excalidraw/excalidraw';
import '@excalidraw/excalidraw/index.css';
import type { ExcalidrawImperativeAPI } from '@excalidraw/excalidraw/types';
import { LayoutTemplate, Trash2 } from 'lucide-react';

export interface WhiteboardDiffPayload {
  element_count: number;
  added_count: number;
  modified_count: number;
  removed_count: number;
  new_labels: string[];
  all_labels: string[];
  summary: string;
}

export interface WhiteboardCapture {
  pngBlob: Blob;
  diff: WhiteboardDiffPayload;
  sceneJson: string;
  elementCount: number;
}

export interface WhiteboardPaneHandle {
  captureSnapshot: () => Promise<WhiteboardCapture | null>;
}

interface SnapshotRecord {
  id: string;
  type: string;
  version: number;
  text: string;
}

function extractActiveElements(api: ExcalidrawImperativeAPI) {
  return api.getSceneElements().filter((el) => !el.isDeleted);
}

export const WhiteboardPane = forwardRef<WhiteboardPaneHandle>(function WhiteboardPane(_, ref) {
  const apiRef = useRef<ExcalidrawImperativeAPI | null>(null);
  const prevElementsRef = useRef<Map<string, SnapshotRecord>>(new Map());
  const [elementCount, setElementCount] = useState(0);

  const captureSnapshot = useCallback(async (): Promise<WhiteboardCapture | null> => {
    const excalidrawAPI = apiRef.current;
    if (!excalidrawAPI) return null;

    const elements = extractActiveElements(excalidrawAPI);
    if (elements.length === 0) {
      return null;
    }

    const appState = excalidrawAPI.getAppState();
    const files = excalidrawAPI.getFiles();

    const pngBlob = await exportToBlob({
      elements,
      appState: {
        ...appState,
        exportWithDarkMode: false,
        exportBackground: true,
        viewBackgroundColor: '#ffffff',
      },
      files,
      mimeType: 'image/png',
      exportPadding: 24,
    });

    const prevMap = prevElementsRef.current;
    const nextMap = new Map<string, SnapshotRecord>();

    let addedCount = 0;
    let modifiedCount = 0;
    const newLabels: string[] = [];
    const allLabels: string[] = [];

    for (const el of elements) {
      const rawText = 'text' in el && typeof el.text === 'string' ? el.text.trim() : '';
      if (rawText) {
        allLabels.push(rawText.replace(/\s+/g, ' ').slice(0, 60));
      }
      const record: SnapshotRecord = {
        id: el.id,
        type: el.type,
        version: el.version,
        text: rawText,
      };
      nextMap.set(el.id, record);

      const prev = prevMap.get(el.id);
      if (!prev) {
        addedCount += 1;
        if (rawText) {
          newLabels.push(rawText.replace(/\s+/g, ' ').slice(0, 60));
        }
      } else if (prev.version !== record.version || prev.text !== record.text) {
        modifiedCount += 1;
        if (rawText && rawText !== prev.text) {
          newLabels.push(rawText.replace(/\s+/g, ' ').slice(0, 60));
        }
      }
    }

    let removedCount = 0;
    for (const id of prevMap.keys()) {
      if (!nextMap.has(id)) {
        removedCount += 1;
      }
    }

    prevElementsRef.current = nextMap;

    const parts: string[] = [];
    if (addedCount > 0) parts.push(`+${addedCount} added`);
    if (modifiedCount > 0) parts.push(`${modifiedCount} updated`);
    if (removedCount > 0) parts.push(`-${removedCount} removed`);
    const labelPart = newLabels.length > 0 ? ` (${newLabels.slice(0, 4).join(', ')})` : '';
    const summary =
      parts.length > 0
        ? `${parts.join(', ')}${labelPart} · ${elements.length} total`
        : `No canvas changes · ${elements.length} total`;

    const sceneJson = serializeAsJSON(elements, appState, files, 'local');

    return {
      pngBlob,
      diff: {
        element_count: elements.length,
        added_count: addedCount,
        modified_count: modifiedCount,
        removed_count: removedCount,
        new_labels: newLabels.slice(0, 10),
        all_labels: allLabels.slice(0, 25),
        summary,
      },
      sceneJson,
      elementCount: elements.length,
    };
  }, []);

  useImperativeHandle(ref, () => ({ captureSnapshot }), [captureSnapshot]);

  const handleInsertStarterFrame = () => {
    const excalidrawAPI = apiRef.current;
    if (!excalidrawAPI) return;
    const now = Date.now();
    const base = {
      angle: 0,
      strokeColor: '#1e293b',
      backgroundColor: '#f8fafc',
      fillStyle: 'solid' as const,
      strokeWidth: 2,
      strokeStyle: 'solid' as const,
      roughness: 1,
      opacity: 100,
      groupIds: [] as string[],
      frameId: null,
      index: null,
      roundness: { type: 3 as const },
      version: 1,
      versionNonce: 1,
      isDeleted: false,
      boundElements: null,
      updated: now,
      link: null,
      locked: false,
    };
    const textBase = {
      ...base,
      backgroundColor: 'transparent',
      roundness: null,
      fontSize: 18,
      fontFamily: 1,
      textAlign: 'left' as const,
      verticalAlign: 'top' as const,
      containerId: null,
      lineHeight: 1.25 as const,
      autoResize: true,
    };

    const starterElements = [
      {
        ...base,
        id: `starter-app-${now}`,
        type: 'rectangle' as const,
        x: 60,
        y: 60,
        width: 560,
        height: 180,
        strokeColor: '#4f46e5',
        backgroundColor: '#eef2ff',
        seed: 101,
      },
      {
        ...textBase,
        id: `starter-app-lbl-${now}`,
        type: 'text' as const,
        x: 80,
        y: 76,
        width: 340,
        height: 24,
        strokeColor: '#3730a3',
        text: 'Application / DX Layer (Docs, Sandbox, MCP Tools)',
        originalText: 'Application / DX Layer (Docs, Sandbox, MCP Tools)',
        seed: 102,
      },
      {
        ...base,
        id: `starter-core-${now}`,
        type: 'rectangle' as const,
        x: 60,
        y: 280,
        width: 560,
        height: 190,
        strokeColor: '#059669',
        backgroundColor: '#ecfdf5',
        seed: 103,
      },
      {
        ...textBase,
        id: `starter-core-lbl-${now}`,
        type: 'text' as const,
        x: 80,
        y: 296,
        width: 420,
        height: 24,
        strokeColor: '#065f46',
        text: 'Core Platform / Gateway Layer (Limits, RBAC, Audit, Rails)',
        originalText: 'Core Platform / Gateway Layer (Limits, RBAC, Audit, Rails)',
        seed: 104,
      },
    ];

    const existing = extractActiveElements(excalidrawAPI);
    excalidrawAPI.updateScene({
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      elements: [...existing, ...(starterElements as any)],
    });
    excalidrawAPI.scrollToContent(undefined, { fitToViewport: true });
  };

  const handleClearCanvas = () => {
    const excalidrawAPI = apiRef.current;
    if (!excalidrawAPI) return;
    excalidrawAPI.resetScene();
    setElementCount(0);
  };

  return (
    <div className="whiteboard-container">
      <div className="whiteboard-toolbar">
        <div className="whiteboard-toolbar-left">
          <span className="wb-status-dot" />
          <span>
            Auto-captured on every Push-to-Talk submit ({elementCount}{' '}
            {elementCount === 1 ? 'element' : 'elements'})
          </span>
        </div>
        <div className="whiteboard-toolbar-actions">
          <button
            type="button"
            className="wb-mini-btn"
            onClick={handleInsertStarterFrame}
            title="Insert Core vs. Application Layer starter frame"
          >
            <LayoutTemplate size={13} /> Starter Frame
          </button>
          <button
            type="button"
            className="wb-mini-btn"
            onClick={handleClearCanvas}
            title="Clear whiteboard"
          >
            <Trash2 size={13} /> Clear
          </button>
        </div>
      </div>

      <div className="excalidraw-host">
        <Excalidraw
          excalidrawAPI={(api) => {
            apiRef.current = api;
          }}
          theme="light"
          onChange={(elements) => {
            const active = elements.filter((el) => !el.isDeleted).length;
            setElementCount((prev) => (prev === active ? prev : active));
          }}
          UIOptions={{
            canvasActions: {
              loadScene: false,
              saveToActiveFile: false,
              export: false,
              toggleTheme: true,
            },
          }}
        />
      </div>
    </div>
  );
});
