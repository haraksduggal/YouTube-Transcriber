# YouTube Transcript & Translation PDF Generator

A Python tool to download, transcribe, and (optionally) translate YouTube videos, generating a timestamped PDF transcript.

---

## 🚀 Features

- **Download audio** from any YouTube video
- **Transcribe** using OpenAI Whisper (tiny, base, small, medium, large)
- **Auto language detection** or force English transcription
- **Translate** transcript to any Google Translate-supported language
- **Timestamped PDF** output with original and translated text
- **Unicode support** with automatic font download
- **Interactive CLI** for easy use

---

## 📦 Installation

1. **Clone the repository:**
    ```
    git clone https://github.com/haraksduggal/youtube-transcript-generator.git
    cd youtube-transcript-generator
    ```

2. **Install dependencies:**
    ```
    pip install torch yt-dlp openai-whisper fpdf tqdm deep-translator requests
    ```

---

## 📝 Usage

Run the script and follow the prompts:

You’ll be asked for:
- The YouTube video URL
- Whisper model size (tiny/base/small/medium/large)
- Whether to force English transcription
- Target language code for translation (optional, e.g. `hi` for Hindi, `fr` for French)

A PDF will be generated in the current folder, titled after the video.

---

## 🖨️ Example Output

- **Video title** as the document header
- **Timestamps** in `[MM:SS-MM:SS]` format
- **Original text** and (optionally) **translated text** for each segment

---

## ⚙️ Advanced Options

- **Model selection**: Larger models = better accuracy, more resources required
- **Force language**: Useful for English videos with mixed content
- **PDF font**: DejaVuSans.ttf auto-downloaded for Unicode support

---

## 💡 Troubleshooting

- If font download fails, Helvetica is used as fallback
- For best results, use high-quality audio and larger Whisper models

---

## 📄 License

MIT License

---

## 🤝 Contributing

Pull requests and suggestions welcome!

---

*Created with ❤️ to make video content accessible in any language.*


