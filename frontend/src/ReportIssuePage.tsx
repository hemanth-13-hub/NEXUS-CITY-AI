import { useEffect, useRef, useState, type FormEvent } from 'react';
import { ArrowRight, Globe2, MapPin, Menu, Plus, ShieldCheck, Sparkles, X } from 'lucide-react';
import { Link, NavLink } from 'react-router-dom';
import { submitReport, ImageUploadError, type ReportDraft } from './offlineReports';
import type { Report } from './api';
import { OfflineStatus } from './OfflineStatus';

const categories = [
  'Flooding',
  'Water Leakage',
  'Waterlogging',
  'Blocked Drainage',
  'Potholes',
  'Road Damage',
  'Streetlight Failure',
  'Landslide Risk',
  'Other Infrastructure Issues',
];

type FormValues = {
  title: string;
  description: string;
  citizen_category: string;
  location_name: string;
  latitude: string;
  longitude: string;
};

export function ReportIssuePage() {
  const [form, setForm] = useState<FormValues>({
    title: '',
    description: '',
    citizen_category: 'Water Leakage',
    location_name: '',
    latitude: '',
    longitude: '',
  });
  const [image, setImage] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [locating, setLocating] = useState(false);
  const [error, setError] = useState('');
  const [created, setCreated] = useState<Report | null>(null);
  const [pendingKey, setPendingKey] = useState('');
  const submissionKey = useRef<string | null>(null);

  useEffect(() => {
    const onReportSynced = (event: Event) => {
      const detail = (event as CustomEvent<{ idempotencyKey: string; report: Report }>).detail;
      if (detail.idempotencyKey === pendingKey) {
        setCreated(detail.report);
        setPendingKey('');
      }
    };
    window.addEventListener('nexus-report-synced', onReportSynced);
    return () => window.removeEventListener('nexus-report-synced', onReportSynced);
  }, [pendingKey]);

  function change(field: keyof FormValues, value: string) {
    setForm(current => ({ ...current, [field]: value }));
  }

  function locate() {
    if (!navigator.geolocation) {
      setError('Location is unavailable. Enter the location manually.');
      return;
    }
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      position => {
        setForm(current => ({
          ...current,
          latitude: position.coords.latitude.toFixed(6),
          longitude: position.coords.longitude.toFixed(6),
          location_name: current.location_name || 'Current location',
        }));
        setLocating(false);
      },
      () => {
        setError('Location permission was not granted. You can enter the location manually.');
        setLocating(false);
      },
      { timeout: 10000 },
    );
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError('');
    const payload: ReportDraft = {
      title: form.title.trim(),
      description: form.description.trim(),
      citizen_category: form.citizen_category,
      location_name: form.location_name.trim(),
      latitude: form.latitude ? Number(form.latitude) : null,
      longitude: form.longitude ? Number(form.longitude) : null,
    };
    submissionKey.current ??= crypto.randomUUID();
    try {
      const result = await submitReport(payload, image, submissionKey.current);
      if (result.state === 'pending') {
        setPendingKey(result.idempotencyKey);
      } else {
        setCreated(result.report);
        submissionKey.current = null;
      }
    } catch (caught) {
      if (caught instanceof ImageUploadError) {
        setCreated(caught.report);
        setError(caught.message);
        submissionKey.current = null;
      } else {
        setError((caught as Error).message);
      }
    } finally {
      setBusy(false);
    }
  }

  function resetForm() {
    setForm({
      title: '',
      description: '',
      citizen_category: 'Water Leakage',
      location_name: '',
      latitude: '',
      longitude: '',
    });
    setImage(null);
    setCreated(null);
    setPendingKey('');
    setError('');
    submissionKey.current = null;
  }

  return (
    <div className="app-shell">
      <OfflineStatus />
      <header className="topbar">
        <Link to="/" className="brand">
          <span className="brand-mark"><Globe2 size={22} /><i /></span>
          <span><b>NEXUS CITY <em>AI</em></b><small>SMART INFRASTRUCTURE</small></span>
        </Link>
        <button className="mobile-menu icon-btn" onClick={() => setMenuOpen(open => !open)} aria-label="Toggle navigation"><Menu /></button>
        <nav className={menuOpen ? 'nav-links open' : 'nav-links'}>
          <NavLink to="/" end>Overview</NavLink>
          <NavLink to="/dashboard">Dashboard</NavLink>
          <NavLink to="/map">Live map</NavLink>
          <NavLink to="/analytics">Analytics</NavLink>
        </nav>
        <div className="header-actions">
          <Link className="track-link" to="/track">Track report</Link>
          <Link className="btn btn-primary btn-sm" to="/report"><Plus size={16} /> Report issue</Link>
        </div>
      </header>
      <main className="main-content narrow-content">
        <div className="page-heading">
          <div>
            <div className="eyebrow"><span /> CITIZEN SERVICES / NEW REPORT</div>
            <h1>Report an issue</h1>
            <p>Help city teams understand an infrastructure problem. Reports made offline are queued on this device until they can be synchronized.</p>
          </div>
        </div>
        <div className="form-layout">
          <form className="panel report-form" onSubmit={submit}>
            <div className="form-section-title"><span>01</span><div><h3>Issue details</h3><p>Describe what needs attention.</p></div></div>
            <label className="field-label">Issue title <span>*</span>
              <input required minLength={5} maxLength={140} value={form.title} onChange={event => change('title', event.target.value)} placeholder="e.g. Water pipe leaking near bus stop" />
            </label>
            <label className="field-label">Infrastructure category <span>*</span>
              <select required value={form.citizen_category} onChange={event => change('citizen_category', event.target.value)}>
                {categories.map(category => <option key={category}>{category}</option>)}
              </select>
            </label>
            <label className="field-label">Description <span>*</span>
              <textarea required minLength={10} maxLength={5000} rows={5} value={form.description} onChange={event => change('description', event.target.value)} placeholder="What happened? How long has it been happening? Is it affecting access or traffic?" />
              <small>Avoid including private or sensitive personal information.</small>
            </label>
            <label className="field-label">Attach a photo (optional)
              <input type="file" accept="image/jpeg,image/png,image/webp,image/gif" disabled={import.meta.env.PROD} onChange={event => {
                const file = event.target.files?.[0] ?? null;
                if (file && file.size > 5 * 1024 * 1024) {
                  setError('Image must be 5 MiB or smaller.');
                  event.currentTarget.value = '';
                  return;
                }
                setError('');
                setImage(file);
              }} />
              <small>{import.meta.env.PROD ? 'Photo uploads are disabled until durable object storage is configured.' : 'JPG, PNG, WEBP, or GIF · max 5 MiB. The photo is stored with the offline report until sync.'}</small>
            </label>
            {image && <div className="image-preview"><span>{image.name}</span><button type="button" className="btn btn-secondary btn-sm" onClick={() => setImage(null)}><X size={14} /> Remove photo</button></div>}
            <div className="form-divider" />
            <div className="form-section-title"><span>02</span><div><h3>Location</h3><p>Help operations teams find the issue.</p></div></div>
            <label className="field-label">Location name or address <span>*</span>
              <input required minLength={2} maxLength={220} value={form.location_name} onChange={event => change('location_name', event.target.value)} placeholder="Street, landmark, or neighbourhood" />
            </label>
            <button type="button" className="btn btn-secondary locate-btn" onClick={locate} disabled={locating}>
              <MapPin size={16} />{locating ? 'Getting location…' : 'Use my current location'}
            </button>
            <div className="two-fields">
              <label className="field-label">Latitude
                <input type="number" step="any" min="-90" max="90" value={form.latitude} onChange={event => change('latitude', event.target.value)} placeholder="17.3850" />
              </label>
              <label className="field-label">Longitude
                <input type="number" step="any" min="-180" max="180" value={form.longitude} onChange={event => change('longitude', event.target.value)} placeholder="78.4867" />
              </label>
            </div>
            <p className="helper-note"><MapPin size={14} /> Coordinates are optional. Location lookup requires permission and a secure context.</p>
            {error && <div className="error-banner"><span>{error}</span></div>}
            <button className="btn btn-primary btn-wide submit-btn" type="submit" disabled={busy}>
              {busy ? 'Saving report…' : 'Submit infrastructure report'} <ArrowRight size={17} />
            </button>
            <p className="fine-print">A report is confirmed as submitted only after the server responds successfully. Offline reports remain pending on this device.</p>
          </form>
          <aside className="form-aside">
            <div className="aside-card ai-aside">
              <span className="aside-icon"><Sparkles size={19} /></span><h3>What happens next?</h3>
              <div className="aside-step"><span>1</span><div><b>Report is recorded</b><p>A unique reference ID is created by the server.</p></div></div>
              <div className="aside-step"><span>2</span><div><b>Preliminary analysis</b><p>Rules suggest a category, severity, and department.</p></div></div>
              <div className="aside-step"><span>3</span><div><b>Review and follow-up</b><p>Use your report ID to track its status.</p></div></div>
            </div>
            <div className="aside-card privacy-card"><ShieldCheck size={18} /><b>Share only what's needed</b><p>Don't include passwords, personal IDs, or sensitive details. This prototype is not an emergency reporting service.</p></div>
          </aside>
        </div>
        {(created || pendingKey) && (
          <div className="modal-backdrop">
            <div className="success-modal" role="dialog" aria-modal="true">
              <button className="modal-close icon-btn" onClick={resetForm} aria-label="Close"><X /></button>
              {created ? (
                <>
                  <div className="eyebrow"><span /> SERVER CONFIRMED</div>
                  <h2>Your report was submitted.</h2>
                  <p>The backend confirmed receipt. Its analysis is a rule-based suggestion and may need human review.</p>
                  <div className="reference-box"><span>YOUR REPORT ID</span><b>{created.public_report_id}</b></div>
                  <div className="modal-actions">
                    <Link className="btn btn-primary" to={`/reports/${created.public_report_id}`}>View report <ArrowRight size={16} /></Link>
                    <Link className="btn btn-secondary" to={`/track?id=${created.public_report_id}`}>Track status</Link>
                  </div>
                </>
              ) : (
                <>
                  <div className="eyebrow"><span /> PENDING SYNC</div>
                  <h2>Saved on this device.</h2>
                  <p>This report has <strong>not</strong> been submitted to the server. It will retry when this device is online and the app is opened.</p>
                  <div className="reference-box"><span>LOCAL SYNC REFERENCE</span><b>{pendingKey.slice(0, 8).toUpperCase()}</b></div>
                  <button type="button" className="btn btn-secondary" onClick={resetForm}>Create another report</button>
                </>
              )}
            </div>
          </div>
        )}
      </main>
      <footer className="footer"><span>One Platform. Every Problem. Smarter Cities.</span><span className="demo-label"><span /> NEXUS CITY AI</span></footer>
    </div>
  );
}
