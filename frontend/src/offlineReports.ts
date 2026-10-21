import { API, NetworkRequestError, request, type Report } from './api';

export type ReportDraft = {
  title: string;
  description: string;
  citizen_category: string;
  location_name: string;
  latitude: number | null;
  longitude: number | null;
};

export type QueuedReport = {
  idempotencyKey: string;
  payload: ReportDraft;
  image?: Blob;
  imageName?: string;
  createdAt: string;
  attempts: number;
  state: 'pending' | 'syncing' | 'failed';
  lastError?: string;
};

type SubmissionResult =
  | { state: 'submitted'; report: Report }
  | { state: 'pending'; idempotencyKey: string };

const databaseName = 'nexus-city-ai-offline';
const storeName = 'pending-reports';
let databasePromise: Promise<IDBDatabase> | undefined;
let syncPromise: Promise<void> | undefined;

function openDatabase(): Promise<IDBDatabase> {
  if (!('indexedDB' in window)) {
    return Promise.reject(new Error('Offline storage is not available in this browser.'));
  }
  databasePromise ??= new Promise((resolve, reject) => {
    const open = indexedDB.open(databaseName, 1);
    open.onupgradeneeded = () => {
      open.result.createObjectStore(storeName, { keyPath: 'idempotencyKey' });
    };
    open.onsuccess = () => resolve(open.result);
    open.onerror = () => reject(open.error ?? new Error('Could not open offline storage.'));
  });
  return databasePromise;
}

async function withStore<T>(
  mode: IDBTransactionMode,
  operation: (store: IDBObjectStore) => IDBRequest<T>,
): Promise<T> {
  const database = await openDatabase();
  return new Promise((resolve, reject) => {
    const transaction = database.transaction(storeName, mode);
    const storeRequest = operation(transaction.objectStore(storeName));
    let result!: T;
    storeRequest.onsuccess = () => {
      result = storeRequest.result;
    };
    storeRequest.onerror = () => reject(storeRequest.error ?? new Error('Offline storage failed.'));
    transaction.oncomplete = () => resolve(result);
    transaction.onabort = () => reject(transaction.error ?? new Error('Offline storage was interrupted.'));
  });
}

function notifyQueueChanged(): void {
  window.dispatchEvent(new Event('nexus-queue-changed'));
}

function notifyReportSynced(idempotencyKey: string, report: Report): void {
  window.dispatchEvent(
    new CustomEvent('nexus-report-synced', { detail: { idempotencyKey, report } }),
  );
}

export async function listQueuedReports(): Promise<QueuedReport[]> {
  return (await withStore('readonly', store => store.getAll())) as QueuedReport[];
}

async function saveQueuedReport(report: QueuedReport): Promise<void> {
  await withStore('readwrite', store => store.put(report));
  notifyQueueChanged();
}

async function removeQueuedReport(idempotencyKey: string): Promise<void> {
  await withStore('readwrite', store => store.delete(idempotencyKey));
  notifyQueueChanged();
}

async function enqueueReport(
  payload: ReportDraft,
  idempotencyKey: string,
  image?: File,
): Promise<void> {
  await saveQueuedReport({
    idempotencyKey,
    payload,
    image,
    imageName: image?.name,
    createdAt: new Date().toISOString(),
    attempts: 0,
    state: 'pending',
  });
}

export class ImageUploadError extends Error {
  constructor(readonly report: Report, message: string) {
    super(message);
    this.name = 'ImageUploadError';
  }
}

export async function submitReport(
  payload: ReportDraft,
  image: File | null,
  idempotencyKey: string,
): Promise<SubmissionResult> {
  if (!navigator.onLine) {
    await enqueueReport(payload, idempotencyKey, image ?? undefined);
    return { state: 'pending', idempotencyKey };
  }

  let report: Report;
  try {
    report = await request<Report>('/api/reports', {
      method: 'POST',
      headers: { 'Idempotency-Key': idempotencyKey },
      body: JSON.stringify(payload),
    });
  } catch (error) {
    if (!(error instanceof NetworkRequestError)) throw error;
    await enqueueReport(payload, idempotencyKey, image ?? undefined);
    return { state: 'pending', idempotencyKey };
  }

  if (image) {
    try {
      await uploadImage(report.public_report_id, image);
      report = await request<Report>(`/api/reports/${report.public_report_id}`);
    } catch (error) {
      throw new ImageUploadError(
        report,
        `Report ${report.public_report_id} was submitted, but its photo could not be uploaded: ${(error as Error).message}`,
      );
    }
  }
  return { state: 'submitted', report };
}

async function uploadImage(reportId: string, image: Blob, imageName = 'report-image'): Promise<void> {
  const form = new FormData();
  form.append('image', image, imageName);
  const response = await fetch(`${API}/api/reports/${reportId}/image`, {
    method: 'POST',
    body: form,
  });
  if (!response.ok) {
    let message = response.statusText || 'Image upload failed';
    try {
      const body = await response.json();
      message = body.detail || message;
    } catch {
      // Keep the HTTP status message when the server did not return JSON.
    }
    throw new Error(message);
  }
}

export async function syncQueuedReports(): Promise<void> {
  if (syncPromise) return syncPromise;
  syncPromise = (async () => {
    if (!navigator.onLine) return;
    const queued = await listQueuedReports();
    for (const report of queued) {
      if (!navigator.onLine) break;
      await saveQueuedReport({ ...report, state: 'syncing', lastError: undefined });
      try {
        const saved = await request<Report>('/api/reports', {
          method: 'POST',
          headers: { 'Idempotency-Key': report.idempotencyKey },
          body: JSON.stringify(report.payload),
        });
        if (report.image) {
          await uploadImage(saved.public_report_id, report.image, report.imageName);
        }
        notifyReportSynced(report.idempotencyKey, saved);
        await removeQueuedReport(report.idempotencyKey);
      } catch (error) {
        await saveQueuedReport({
          ...report,
          attempts: report.attempts + 1,
          state: 'failed',
          lastError: (error as Error).message,
        });
      }
    }
  })().finally(() => {
    syncPromise = undefined;
  });
  return syncPromise;
}
