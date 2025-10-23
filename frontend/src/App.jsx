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
  };

  const onDrop = (e) => {
    e.preventDefault();
    const f = e.dataTransfer.files?.[0];
    if (f) onFileSelected(f);
  };

  const onChoose = () => fileInputRef.current?.click();

  const submit = async () => {
    if (!file) return setError("Please choose a PDF file.");
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      if (issuer) fd.append("issuer", issuer);

      const res = await fetch("https://sure-financial.onrender.com/parse", {
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
  };

  const clear = () => {
    setFile(null);
    setIssuer("");
    setResult(null);
    setError("");
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-3 sm:p-6">
      <div className="w-full max-w-3xl bg-white rounded-xl shadow-lg p-4 sm:p-6">
        <header className="mb-4 sm:mb-6">
          <h1 className="text-xl sm:text-2xl font-semibold text-slate-800">Credit Card Statement Parser</h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">Upload a PDF statement and extract key fields (issuer, last4, billing period, due date).</p>
        </header>

        {/* File Upload Section - Responsive Layout */}
        <div
          onDrop={onDrop}
          onDragOver={(e) => e.preventDefault()}
          className="border-2 border-dashed border-slate-200 rounded-lg p-3 sm:p-6 flex flex-col md:flex-row gap-4"
        >
          {/* Left Section - File Selection */}
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

              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 sm:p-3 bg-indigo-50 rounded-md">
                    <svg className="w-5 h-5 sm:w-6 sm:h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M12 8v8m4-4H8" />
                    </svg>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-slate-700 truncate max-w-[200px] sm:max-w-[300px]">
                      {file ? file.name : "No file selected"}
                    </div>
                    <div className="text-xs text-slate-400">
                      {file ? `${(file.size/1024).toFixed(1)} KB` : "Drag & drop or choose a file"}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 mt-2 sm:mt-0">
                  <button
                    onClick={onChoose}
                    className="px-3 py-1.5 sm:px-4 sm:py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 text-xs sm:text-sm flex-1 sm:flex-none text-center"
                  >
                    Choose
                  </button>
                  {file && (
                    <button
                      onClick={() => setFile(null)}
                      className="px-3 py-1.5 sm:px-3 sm:py-2 border rounded-md text-xs sm:text-sm text-slate-600 hover:bg-slate-50"
                    >
                      Remove
                    </button>
                  )}
                </div>
              </div>

              <div className="mt-2 text-xs text-slate-400">Tip: For scanned PDFs, OCR may be required.</div>
            </div>
          </div>

          {/* Right Section - Issuer & Actions */}
          <div className="w-full md:w-56 mt-2 md:mt-0">
            <label className="block text-sm font-medium text-slate-600 mb-2">Issuer (optional)</label>
            <input
              value={issuer}
              onChange={(e) => setIssuer(e.target.value)}
              placeholder="e.g., HDFC Bank"
              className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-200"
            />
            <div className="mt-3 flex gap-2">
              <button
                onClick={submit}
                disabled={loading || !file}
                className="flex-1 px-3 py-2 bg-emerald-600 text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed text-xs sm:text-sm"
              >
                {loading ? (
                  <span className="inline-flex items-center justify-center gap-2">
                    <svg className="w-3 h-3 sm:w-4 sm:h-4 animate-spin" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                    </svg>
                    Parsing...
                  </span>
                ) : (
                  "Upload & Parse"
                )}
              </button>

              <button 
                onClick={clear} 
                className="px-3 py-2 border rounded-md text-xs sm:text-sm text-slate-600"
              >
                Clear
              </button>
            </div>
          </div>
        </div>

        {/* Error & Results Area */}
        <main className="mt-4 sm:mt-6">
          {error && (
            <div className="bg-red-50 border-l-4 border-red-400 text-red-700 p-3 rounded mb-4 text-xs sm:text-sm">
              {error}
            </div>
          )}

          {result ? (
            <div className="grid grid-cols-1 gap-4">
              {/* Parsed Fields */}
              <div className="bg-white border rounded-lg p-4 shadow-sm">
                <h3 className="font-medium text-slate-700 mb-3 text-sm sm:text-base">Parsed fields</h3>
                <dl className="grid grid-cols-2 sm:grid-cols-3 gap-x-2 gap-y-3 text-xs sm:text-sm text-slate-600">
                  <div>
                    <dt className="font-semibold text-slate-800">Issuer</dt>
                    <dd className="mt-0.5 break-words">{result.issuer ?? "—"}</dd>
                  </div>
                  <div>
                    <dt className="font-semibold text-slate-800">Card last 4</dt>
                    <dd className="mt-0.5">{result.card_last4 ?? "—"}</dd>
                  </div>
                  <div>
                    <dt className="font-semibold text-slate-800">Card type</dt>
                    <dd className="mt-0.5 break-words">{result.card_type ?? "—"}</dd>
                  </div>
                  <div className="col-span-2">
                    <dt className="font-semibold text-slate-800">Billing period</dt>
                    <dd className="mt-0.5">{result.billing_period ?? "—"}</dd>
                  </div>
                  <div>
                    <dt className="font-semibold text-slate-800">Due date</dt>
                    <dd className="mt-0.5">{result.payment_due_date ?? "—"}</dd>
                  </div>
                  <div>
                    <dt className="font-semibold text-slate-800">Confidence</dt>
                    <dd className="mt-1">
                      <div className="w-full bg-gray-200 rounded-full h-1.5">
                        <div 
                          className={`h-1.5 rounded-full ${
                            result.confidence > 0.7 ? 'bg-green-500' : 
                            result.confidence > 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${result.confidence * 100}%` }}
                        />
                      </div>
                      <span className="text-xs mt-0.5 inline-block">
                        {Math.round(result.confidence * 100)}%
                      </span>
                    </dd>
                  </div>
                </dl>
              </div>

              {/* Raw Text & JSON - Tabs for Mobile */}
              <div className="mt-2">
                <div className="sm:hidden">
                  <select 
                    id="tabs" 
                    name="tabs"
                    className="block w-full rounded-md border-gray-300 text-xs"
                    defaultValue="snippet"
                    onChange={(e) => {
                      document.getElementById(e.target.value).classList.remove('hidden');
                      ['snippet', 'json'].filter(t => t !== e.target.value).forEach(tab => {
                        document.getElementById(tab).classList.add('hidden');
                      });
                    }}
                  >
                    <option value="snippet">Raw Text Snippet</option>
                    <option value="json">Full JSON</option>
                  </select>
                </div>
                
                {/* Tab Content */}
                <div className="mt-2">
                  {/* Raw Text */}
                  <div id="snippet" className="bg-slate-50 border rounded-lg p-3 shadow-sm overflow-auto h-32 sm:h-48">
                    <h3 className="font-medium text-slate-700 mb-2 text-xs sm:text-sm">Raw text snippet</h3>
                    <pre className="text-xs text-slate-700 whitespace-pre-wrap">{result.raw_text_snippet ?? "—"}</pre>
                  </div>

                  {/* Full JSON - Hidden on Mobile */}
                  <div id="json" className="hidden sm:block mt-4">
                    <h3 className="font-medium text-slate-700 mb-2 text-xs sm:text-sm">Full JSON</h3>
                    <pre className="text-xs bg-black text-green-200 rounded p-3 overflow-auto h-48">{JSON.stringify(result, null, 2)}</pre>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-xs sm:text-sm text-slate-500 py-4 text-center">
              No result yet. Upload a statement to parse.
            </div>
          )}
        </main>

        <footer className="mt-4 sm:mt-6 text-xs text-slate-400 text-center">
          Credit Card Statement Parser • Demo
        </footer>
      </div>
    </div>
  );
}