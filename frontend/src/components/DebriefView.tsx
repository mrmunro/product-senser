import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ArrowLeft, Check, Copy, Download, FileText, MessageSquare } from 'lucide-react';
import type { SessionState } from '../types';

interface DebriefViewProps {
  session: SessionState;
  onBackToLobby: () => void;
}

function formatClock(totalSeconds: number): string {
  const m = Math.floor(totalSeconds / 60);
  const s = totalSeconds % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

export function DebriefView({ session, onBackToLobby }: DebriefViewProps) {
  const [tab, setTab] = useState<'debrief' | 'transcript'>('debrief');
  const [copied, setCopied] = useState(false);

  const markdown = session.debrief_markdown || '_No debrief generated._';

  const handleCopy = async () => {
    await navigator.clipboard.writeText(markdown);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${session.session_id}-debrief.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="debrief-shell">
      <header className="room-topbar">
        <div className="room-title-block">
          <button type="button" className="ghost-btn" onClick={onBackToLobby}>
            <ArrowLeft size={15} /> Back to Lobby
          </button>
          <div>
            <div className="room-case-title">Post-Interview Debrief · {session.title}</div>
            <div className="room-case-sub">
              Saved to <code>sessions/{session.session_id}/debrief.md</code>
            </div>
          </div>
        </div>

        <div className="room-topbar-right">
          <button type="button" className="ghost-btn" onClick={() => void handleCopy()}>
            {copied ? <Check size={15} /> : <Copy size={15} />}
            <span>{copied ? 'Copied' : 'Copy Markdown'}</span>
          </button>
          <button type="button" className="primary-btn" onClick={handleDownload}>
            <Download size={15} />
            <span>Download debrief.md</span>
          </button>
        </div>
      </header>

      <div className="debrief-content">
        <div className="pane-tabs debrief-tabs">
          <button
            type="button"
            className={`tab-btn ${tab === 'debrief' ? 'active' : ''}`}
            onClick={() => setTab('debrief')}
          >
            <FileText size={15} /> Scored Debrief
          </button>
          <button
            type="button"
            className={`tab-btn ${tab === 'transcript' ? 'active' : ''}`}
            onClick={() => setTab('transcript')}
          >
            <MessageSquare size={15} /> Full Transcript ({session.turns.length} turns)
          </button>
        </div>

        {tab === 'debrief' ? (
          <article className="debrief-card markdown-body">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
          </article>
        ) : (
          <div className="debrief-card transcript-archive">
            {session.turns.map((turn) => (
              <div key={turn.id} className={`turn-bubble ${turn.role}`}>
                <div className="turn-header">
                  <strong>
                    {turn.speaker_name} {turn.speaker_role ? `(${turn.speaker_role})` : ''}
                  </strong>
                  <span className="muted">
                    {formatClock(turn.elapsed_seconds)} · {turn.phase}
                    {turn.speaking_duration_seconds > 0
                      ? ` · spoke ${Math.round(turn.speaking_duration_seconds)}s`
                      : ''}
                  </span>
                </div>
                <p className="turn-text">{turn.text}</p>
                {turn.delivery_notes && (
                  <p className="delivery-note">Delivery note: {turn.delivery_notes}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
