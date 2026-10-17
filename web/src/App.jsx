import { useEffect, useRef, useState } from "react";
import {
  ArrowDown,
  ArrowUp,
  BookOpenText,
  Check,
  FileCheck2,
  FileText,
  LoaderCircle,
  MessageSquareText,
  Plus,
  Sparkles,
  Upload,
  X,
} from "lucide-react";

const API = "/api/v1";

function formatBytes(bytes) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function makeMessage(role, text, sources = []) {
  return { id: crypto.randomUUID(), role, text, sources };
}

export default function App() {
  const [document, setDocument] = useState(null);
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [uploading, setUploading] = useState(false);
  const [thinking, setThinking] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState("");
  const fileInput = useRef(null);
  const endOfMessages = useRef(null);

  useEffect(() => {
    endOfMessages.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, thinking]);

  async function uploadPdf(file) {
    if (!file) return;
    setError("");
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Choose a PDF file to start a document chat.");
      return;
    }

    setUploading(true);
    const body = new FormData();
    body.append("file", file);
    try {
      const response = await fetch(`${API}/documents`, { method: "POST", body });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || "This PDF could not be indexed.");
      setDocument({ ...result, size: file.size });
      setMessages([
        makeMessage(
          "assistant",
          `I've read **${result.filename}**. It has ${result.page_count} pages and is ready for questions.`,
        ),
      ]);
      setDraft("");
    } catch (uploadError) {
      setError(uploadError.message || "Upload failed. Check that the API is running.");
    } finally {
      setUploading(false);
      if (fileInput.current) fileInput.current.value = "";
    }
  }

  async function sendMessage(event) {
    event.preventDefault();
    const question = draft.trim();
    if (!question || !document || thinking) return;

    setError("");
    setDraft("");
    setMessages((current) => [...current, makeMessage("user", question)]);
    setThinking(true);
    try {
      const response = await fetch(`${API}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || "The answer could not be generated.");
      setMessages((current) => [...current, makeMessage("assistant", result.answer, result.sources)]);
    } catch (chatError) {
      setError(chatError.message || "Chat request failed. Check that the API is running.");
      setDraft(question);
    } finally {
      setThinking(false);
    }
  }

  function startNewDocument() {
    setDocument(null);
    setMessages([]);
    setDraft("");
    setError("");
    fileInput.current?.click();
  }

  function onDrop(event) {
    event.preventDefault();
    setDragging(false);
    uploadPdf(event.dataTransfer.files?.[0]);
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#top" aria-label="Papertrail home">
          <span className="brand-mark"><BookOpenText size={19} strokeWidth={2.1} /></span>
          <span>papertrail<span className="brand-period">.</span></span>
        </a>

        <div className="sidebar-section-label">WORKSPACE</div>
        <button className="side-link active" type="button">
          <MessageSquareText size={17} />
          <span>Document chat</span>
          <span className="active-dot" />
        </button>

        <div className="library-heading">
          <span className="sidebar-section-label">CURRENT DOCUMENT</span>
          {document && (
            <button className="icon-button side-add" type="button" onClick={startNewDocument}
              title="Upload another PDF" aria-label="Upload another PDF">
              <Plus size={16} />
            </button>
          )}
        </div>

        {document ? (
          <div className="document-card">
            <div className="document-icon"><FileText size={19} /></div>
            <div className="document-info">
              <span className="document-name" title={document.filename}>{document.filename}</span>
              <span className="document-meta">{document.page_count} pages · {formatBytes(document.size)}</span>
            </div>
            <span className="document-ready" title="Indexed and ready"><Check size={13} /></span>
          </div>
        ) : (
          <button className="sidebar-upload" type="button" onClick={() => fileInput.current?.click()}>
            <Upload size={16} />
            <span>Add a PDF</span>
          </button>
        )}

        <div className="sidebar-spacer" />
        <div className="sidebar-note">
          <span className="note-orbit"><Sparkles size={15} /></span>
          <span>Answers grounded in your document, with page references.</span>
        </div>
        <div className="sidebar-footer"><span className="status-led" /> PRIVATE WORKSPACE</div>
      </aside>

      <main className="main-panel" id="top">
        <header className="topbar">
          <div className="breadcrumb"><span>Workspace</span><span className="crumb-slash">/</span><strong>Document chat</strong></div>
          <div className="topbar-actions">
            <span className={`connection-status ${document ? "ready" : ""}`}>
              <span className="status-led" />
              {document ? "Document ready" : "Waiting for a document"}
            </span>
            <button className="top-upload" type="button" onClick={() => fileInput.current?.click()} disabled={uploading}>
              {uploading ? <LoaderCircle className="spin" size={16} /> : <Upload size={16} />}
              <span>{uploading ? "Indexing…" : document ? "Replace PDF" : "Upload PDF"}</span>
            </button>
          </div>
        </header>

        <input
          ref={fileInput}
          className="visually-hidden"
          type="file"
          accept="application/pdf,.pdf"
          onChange={(event) => uploadPdf(event.target.files?.[0])}
        />

        <section
          className={`conversation ${dragging ? "dragging" : ""}`}
          onDragOver={(event) => { event.preventDefault(); setDragging(true); }}
          onDragLeave={(event) => {
            if (!event.currentTarget.contains(event.relatedTarget)) setDragging(false);
          }}
          onDrop={onDrop}
        >
          {dragging && <div className="drop-overlay"><Upload size={24} /><span>Drop PDF to add it</span></div>}
          {!document ? (
            <div className="empty-state">
              <div className="empty-kicker"><span className="kicker-line" /> YOUR READING DESK</div>
              <div className="empty-symbol"><FileCheck2 size={28} strokeWidth={1.6} /></div>
              <h1>Make sense of<br /><em>the fine print.</em></h1>
              <p>Start with a PDF. Ask a question, find a detail, or get the short version.</p>
              <button className="upload-zone" type="button" onClick={() => fileInput.current?.click()} disabled={uploading}>
                <span className="upload-zone-icon">
                  {uploading ? <LoaderCircle className="spin" size={21} /> : <Upload size={20} />}
                </span>
                <span className="upload-zone-copy">
                  <strong>{uploading ? "Reading your PDF…" : "Choose a PDF to begin"}</strong>
                  <small>or drop it anywhere in this window · up to 20 MB</small>
                </span>
                <span className="upload-zone-arrow"><ArrowDown size={17} /></span>
              </button>
              {error && <div className="error-message" role="alert"><X size={15} />{error}</div>}
              <div className="privacy-note"><span className="privacy-dot" /> Documents use the Pinecone namespace configured for this app</div>
            </div>
          ) : (
            <div className="message-list">
              <div className="conversation-date"><span />TODAY<span /></div>
              {messages.map((message) => (
                <article className={`message-row ${message.role}`} key={message.id}>
                  {message.role === "assistant" ? (
                    <div className="assistant-avatar"><Sparkles size={16} /></div>
                  ) : <div className="user-avatar">Y</div>}
                  <div className="message-body">
                    <div className="message-label">{message.role === "assistant" ? "PAPERTRAIL" : "YOU"}</div>
                    <p>{message.text.split(/(\*\*.*?\*\*)/g).map((part, index) =>
                      part.startsWith("**") && part.endsWith("**")
                        ? <strong key={index}>{part.slice(2, -2)}</strong>
                        : part
                    )}</p>
                    {message.sources?.length > 0 && (
                      <div className="sources-list">
                        <span className="sources-label">SOURCES</span>
                        {message.sources.map((source, index) => (
                          <span className="source-pill" key={`${source.source}-${source.page}-${index}`}>
                            <FileText size={12} />{source.source} <span>p. {source.page}</span>
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </article>
              ))}
              {thinking && (
                <article className="message-row assistant thinking-row">
                  <div className="assistant-avatar"><Sparkles size={16} /></div>
                  <div className="message-body">
                    <div className="message-label">PAPERTRAIL</div>
                    <div className="thinking-indicator"><i /><i /><i /></div>
                  </div>
                </article>
              )}
              <div ref={endOfMessages} />
            </div>
          )}
        </section>

        <footer className="composer-area">
          {error && document && <div className="composer-error" role="alert"><X size={14} />{error}</div>}
          <form className={`composer ${!document ? "disabled" : ""}`} onSubmit={sendMessage}>
            <textarea
              aria-label="Ask a question about the PDF"
              placeholder={document ? "Ask anything about this document…" : "Upload a PDF to start asking questions"}
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  event.currentTarget.form.requestSubmit();
                }
              }}
              rows={1}
              disabled={!document || thinking}
            />
            <div className="composer-bottom">
              <span className="composer-hint"><Sparkles size={13} /> Answers use only this PDF</span>
              <button className="send-button" type="submit" aria-label="Send message"
                title="Send message" disabled={!document || !draft.trim() || thinking}>
                {thinking ? <LoaderCircle className="spin" size={17} /> : <ArrowUp size={18} />}
              </button>
            </div>
          </form>
          <div className="disclaimer">AI can make mistakes. Check important details against the original document.</div>
        </footer>
      </main>
    </div>
  );
}