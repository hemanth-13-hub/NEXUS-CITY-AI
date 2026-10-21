import { useCallback, useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, CloudOff, RefreshCw, Wifi } from 'lucide-react';
import {
  listQueuedReports,
  syncQueuedReports,
  type QueuedReport,
} from './offlineReports';

export function OfflineStatus() {
  const [online, setOnline] = useState(navigator.onLine);
  const [queued, setQueued] = useState<QueuedReport[]>([]);
  const [syncing, setSyncing] = useState(false);
  const [storageError, setStorageError] = useState('');

  const refresh = useCallback(async () => {
    try {
      setQueued(await listQueuedReports());
      setStorageError('');
    } catch (error) {
      setStorageError((error as Error).message);
    }
  }, []);

  const sync = useCallback(async () => {
    if (!navigator.onLine) return;
    setSyncing(true);
    try {
      await syncQueuedReports();
      await refresh();
    } catch (error) {
      setStorageError((error as Error).message);
    } finally {
      setSyncing(false);
    }
  }, [refresh]);

  useEffect(() => {
    const onOnline = () => {
      setOnline(true);
      void sync();
    };
    const onOffline = () => setOnline(false);
    const onNetworkUnavailable = () => setOnline(false);
    const onNetworkAvailable = () => setOnline(true);
    const onFocus = () => {
      void refresh();
      if (navigator.onLine) void sync();
    };
    const onQueueChange = () => void refresh();
    window.addEventListener('online', onOnline);
    window.addEventListener('offline', onOffline);
    window.addEventListener('nexus-network-unavailable', onNetworkUnavailable);
    window.addEventListener('nexus-network-available', onNetworkAvailable);
    window.addEventListener('pageshow', onFocus);
    window.addEventListener('nexus-queue-changed', onQueueChange);
    document.addEventListener('visibilitychange', onFocus);
    void refresh().then(() => {
      if (navigator.onLine) void sync();
    });
    return () => {
      window.removeEventListener('online', onOnline);
      window.removeEventListener('offline', onOffline);
      window.removeEventListener('nexus-network-unavailable', onNetworkUnavailable);
      window.removeEventListener('nexus-network-available', onNetworkAvailable);
      window.removeEventListener('pageshow', onFocus);
      window.removeEventListener('nexus-queue-changed', onQueueChange);
      document.removeEventListener('visibilitychange', onFocus);
    };
  }, [refresh, sync]);

  const failed = queued.filter(report => report.state === 'failed');
  return (
    <section className={`connection-status ${online ? 'is-online' : 'is-offline'}`} aria-live="polite">
      <div className="connection-summary">
        {online ? <Wifi size={16} /> : <CloudOff size={16} />}
        <span>{online ? 'Online' : 'Offline'} · {queued.length} pending {queued.length === 1 ? 'report' : 'reports'}</span>
        {navigator.onLine && queued.length > 0 && (
          <button type="button" className="connection-retry" onClick={() => void sync()} disabled={syncing}>
            <RefreshCw size={14} className={syncing ? 'spin-icon' : ''} />
            {syncing ? 'Syncing…' : 'Sync now'}
          </button>
        )}
        {online && queued.length === 0 && <CheckCircle2 size={16} className="sync-complete-icon" />}
      </div>
      {!online && queued.length > 0 && (
        <p>Reports are saved on this device only. They have not been submitted to the server.</p>
      )}
      {failed.length > 0 && (
        <p className="connection-error"><AlertTriangle size={14} /> {failed.length} report(s) need attention: {failed[0].lastError}</p>
      )}
      {storageError && <p className="connection-error"><AlertTriangle size={14} /> {storageError}</p>}
    </section>
  );
}
