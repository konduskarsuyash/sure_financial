import React, { useState, useRef } from "react";


export default function App() {
  const [file, setFile] = useState(null);
  const [issuer, setIssuer] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const fileInputRef = useRef();


  const onFileSelected = (f) => {
    setError("");
    setResult(null);
    setFile(f);
  }


  const onDrop = (e) => {
    e.preventDefault();
    const f = e.dataTransfer.files?.[0];
    if (f) onFileSelected(f);
  }


  const onChoose = () => fileInputRef.current?.click()


  const submit = async () => {
    if (!file) return setError("Please choose a PDF file.");
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      if (issuer) fd.append("issuer", issuer);


      const res = await fetch("http://127.0.0.1:8000/parse", {
        method: "POST",
        body: fd,
      });
      if (!res.ok) {
        const j = await res.json().catch(() => ({}));
        throw new Error(j.detail || `Server returned ${res.status}`);
      }
      const json = await res.json();
      setResult(json);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }


  const clear = () => {
    setFile(null);
    setIssuer("");
    setResult(null);
    setError("");
  }


  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <div className="w-full max-w-3xl bg-white rounded-xl shadow-lg p-6">
        <header className="mb-6">
          <h1 className="text-2xl font-semibold text-slate-800">Credit Card Statement Parser</h1>
          <p className="text-sm text-slate-500 mt-1">Upload a PDF statement and extract key fields (issuer, last4, billing period, due date).</p>
        </header>


        <div
          onDrop={onDrop}
          onDragOver={(e) => e.preventDefault()}
          className="border-2 border-dashed border-slate-200 rounded-lg p-6 flex gap-4 items-center"
        >
          <div className="flex-1">
            <label className="block text-sm font-medium text-slate-600 mb-2">Statement (PDF)</label>


            <div className="relative">
              <input
                ref={fileInputRef}
                type="file"
                accept="application/pdf"
                className="hidden"
                onChange={(e) => onFileSelected(e.target.files?.[0])}
              />


              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-indigo-50 rounded-md">
                    <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M12 8v8m4-4H8" />
                    </svg>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-slate-700">{file ? file.name : "No file selected"}</div>
                    <div className="text-xs text-slate-400">{file ? `${(file.size/1024).toFixed(1)} KB` : "Drag & drop or choose a file"}</div>
                  </div>
                </div>


                <div className="flex items-center gap-2">
                  <button
                    onClick={onChoose}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 text-sm"
                  >
                    Choose
                  </button>
                  <button
                    onClick={() => setFile(null)}
                    className="px-3 py-2 border rounded-md text-sm text-slate-600 hover:bg-slate-50"
                  >
                    Remove
                  </button>
                </div>
              </div>


              <div className="mt-3 text-xs text-slate-400">Tip: For scanned PDFs, OCR may be required.</div>
            </div>
          </div>


          <div className="w-56">
            <label className="block text-sm font-medium text-slate-600 mb-2">Issuer (optional)</label>
            <input
              value={issuer}
              onChange={(e) => setIssuer(e.target.value)}
              placeholder="e.g., Chase"
              className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-200"
            />
            <div className="mt-3 flex gap-2">
              <button
                onClick={submit}
                disabled={loading || !file}
                className="flex-1 px-3 py-2 bg-emerald-600 text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <span className="inline-flex items-center gap-2">
                    <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                    </svg>
                    Parsing...
                  </span>
                ) : (
                  "Upload & Parse"
                )}
              </button>


              <button onClick={clear} className="px-3 py-2 border rounded-md text-sm">
                Clear
              </button>
            </div>
          </div>
        </div>


        <main className="mt-6">
          {error && <div className="bg-red-50 border-l-4 border-red-400 text-red-700 p-3 rounded mb-4">{error}</div>}


          {result ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white border rounded-lg p-4 shadow-sm">
                <h3 className="font-medium text-slate-700 mb-3">Parsed fields</h3>
                <dl className="text-sm text-slate-600 space-y-2">
                  <div><dt className="font-semibold text-slate-800">Issuer</dt><dd>{result.issuer ?? "—"}</dd></div>
                  <div><dt className="font-semibold text-slate-800">Card last 4</dt><dd>{result.card_last4 ?? "—"}</dd></div>
                  <div><dt className="font-semibold text-slate-800">Card type</dt><dd>{result.card_type ?? "—"}</dd></div>
                  <div><dt className="font-semibold text-slate-800">Billing period</dt><dd>{result.billing_period ?? "—"}</dd></div>
                  <div><dt className="font-semibold text-slate-800">Payment due date</dt><dd>{result.payment_due_date ?? "—"}</dd></div>
                  <div><dt className="font-semibold text-slate-800">Confidence</dt><dd>{result.confidence ?? "—"}</dd></div>
                </dl>
              </div>


              <div className="bg-slate-50 border rounded-lg p-4 shadow-sm overflow-auto">
                <h3 className="font-medium text-slate-700 mb-3">Raw text snippet</h3>
                <pre className="text-xs text-slate-700 whitespace-pre-wrap">{result.raw_text_snippet ?? "—"}</pre>
              </div>


              <div className="md:col-span-2">
                <h3 className="font-medium text-slate-700 mb-2">Full JSON</h3>
                <pre className="text-xs bg-black text-green-200 rounded p-3 overflow-auto">{JSON.stringify(result, null, 2)}</pre>
              </div>
            </div>
          ) : (
            <div className="text-sm text-slate-500">No result yet. Upload a statement to parse.</div>
          )}
        </main>


        <footer className="mt-6 text-xs text-slate-400">
          Note: This UI is a demo. For production enable HTTPS and proper CORS, file scanning, and error handling.
        </footer>
      </div>
    </div>
  );
}