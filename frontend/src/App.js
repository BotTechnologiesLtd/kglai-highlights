import { useState } from "react";

function App() {
  const [video, setVideo] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [highlight, setHighlight] = useState(null);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setVideo(URL.createObjectURL(file));
    setProcessing(true);

    const formData = new FormData();
    formData.append("file", file);
    
# TODO: ADD BACK END LINK
    const res = await fetch("https://your-backend-host.onrender.com/process", {
      method: "POST",
      body: formData,
    });

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    setHighlight(url);
    setProcessing(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-6">
      <div className="max-w-2xl w-full shadow-xl rounded-2xl p-6 bg-white">
        <h1 className="text-3xl font-bold text-center text-green-700 mb-4">
          ⚽ GoalAI Highlights
        </h1>
        <p className="text-center mb-6 text-gray-600">
          Upload your football match video and get AI-powered highlights (max 3 minutes).
        </p>

        <input
          type="file"
          accept="video/*"
          onChange={handleUpload}
          className="mb-4"
        />

        {video && <video controls src={video} className="rounded-xl w-full mb-4" />}

        {processing && <p className="text-center text-blue-600">⏳ Processing...</p>}

        {highlight && (
          <div className="space-y-4">
            <video controls src={highlight} className="rounded-xl w-full" />
            <a
              href={highlight}
              download="kglai_highlights.mp4"
              className="block text-center bg-green-600 text-white py-2 rounded-xl"
            >
              ⬇️ Download Highlights
            </a>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
