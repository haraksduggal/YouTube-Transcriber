import os
import shutil
import torch
import yt_dlp
import whisper
from fpdf import FPDF
from tqdm import tqdm
from deep_translator import GoogleTranslator
import requests

# Format timestamp range
def format_timestamp_range(start_seconds, end_seconds):
    """Format start and end timestamps into [MM:SS-MM:SS]"""
    start_min = int(start_seconds) // 60
    start_sec = int(start_seconds) % 60
    end_min = int(end_seconds) // 60
    end_sec = int(end_seconds) % 60
    return f"[{start_min:02}:{start_sec:02}-{end_min:02}:{end_sec:02}]"

# Download audio
def download_audio(video_url):
    print("\n🎵 Downloading audio...")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloaded_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
        'noplaylist': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_title = info.get('title', 'audio')
        return 'downloaded_audio.mp3', video_title
    except Exception as e:
        print(f"❌ Error downloading audio: {e}")
        exit()

# Transcribe audio
def transcribe_audio(audio_path, model_name="base", force_language=None):
    print("\n📝 Transcribing audio...")
    model = whisper.load_model(model_name)
    options = {}
    if force_language:
        options["language"] = force_language
    result = model.transcribe(audio_path, **options)
    return result["segments"], result.get("language", "unknown")

# Translate segments
def translate_segments(segments, target_lang_code):
    print("\n🌎 Translating segments...")
    translated_segments = []
    for segment in tqdm(segments, desc="Translating"):
        try:
            translated_text = GoogleTranslator(source="auto", target=target_lang_code).translate(segment['text'])
        except Exception as e:
            print(f"❌ Translation error: {e}")
            translated_text = segment['text']
        translated_segments.append({
            'start': segment['start'],
            'end': segment['end'],
            'text': translated_text
        })
    return translated_segments

# Setup font
def setup_font(pdf):
    project_font_path = 'DejaVuSans.ttf'
    if not os.path.exists(project_font_path):
        print("⬇️  DejaVuSans.ttf not found, downloading...")
        url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
        response = requests.get(url)
        with open(project_font_path, 'wb') as f:
            f.write(response.content)
        print("✅ Font downloaded successfully.")

    try:
        pdf.add_font('DejaVu', '', project_font_path, uni=True)
        pdf.set_font('DejaVu', size=11)
        pdf.custom_font_loaded = True
        print("✅ Custom Unicode font loaded.")
    except Exception as e:
        print(f"⚠️ Error loading custom font: {e}")
        print("⚠️ Using default font (Helvetica).")
        pdf.set_font('Helvetica', size=11)
        pdf.custom_font_loaded = False

# Custom PDF class
class PDF(FPDF):
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.set_auto_page_break(auto=True, margin=15)
        setup_font(self)
        self.add_page()

    def header(self):
        # Title above the line, centered
        if getattr(self, "custom_font_loaded", False):
            self.set_font('DejaVu', '', 16)
        else:
            self.set_font('Helvetica', '', 16)

        self.set_text_color(30, 30, 30)
        self.cell(0, 10, self.title, align="C", ln=True)
        self.ln(2)
        # Draw the line below the title
        self.set_draw_color(100, 100, 100)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def add_segment(self, timestamp, original_text, translated_text=None):
        # Timestamp (bold)
        if getattr(self, "custom_font_loaded", False):
            self.set_font('DejaVu', 'B', 11)
        else:
            self.set_font('Helvetica', 'B', 11)
        self.cell(0, 8, timestamp, ln=True)

        # Original label and text (no indentation)
        if getattr(self, "custom_font_loaded", False):
            self.set_font('DejaVu', 'B', 11)
        else:
            self.set_font('Helvetica', 'B', 11)
        self.cell(0, 8, "Original:", ln=True)

        if getattr(self, "custom_font_loaded", False):
            self.set_font('DejaVu', '', 11)
        else:
            self.set_font('Helvetica', '', 11)
        self.multi_cell(0, 8, original_text)

        # Translated label and text (no indentation)
        if translated_text:
            self.ln(2)
            if getattr(self, "custom_font_loaded", False):
                self.set_font('DejaVu', 'B', 11)
            else:
                self.set_font('Helvetica', 'B', 11)
            self.cell(0, 8, "Translated:", ln=True)

            if getattr(self, "custom_font_loaded", False):
                self.set_font('DejaVu', '', 11)
            else:
                self.set_font('Helvetica', '', 11)
            self.multi_cell(0, 8, translated_text)

        self.ln(6)

# Save to PDF
def save_to_pdf(segments, translated_segments, title, translation_enabled):
    print("\n📄 Saving to PDF...")
    pdf = PDF(title=title)

    for i, segment in enumerate(segments):
        timestamp = format_timestamp_range(segment['start'], segment['end'])
        original_text = segment['text']
        translated_text = None

        if translation_enabled and translated_segments:
            translated_text = translated_segments[i]['text']

        pdf.add_segment(timestamp, original_text, translated_text)

    output_path = f"{title}.pdf".replace("/", "-").replace("\\", "-")
    pdf.output(output_path)
    print(f"✅ PDF saved as '{output_path}'.")

# Cleanup temp files
def cleanup(audio_path):
    if os.path.exists(audio_path):
        os.remove(audio_path)
        print("🧹 Temporary files cleaned up.")

# Main function
def process_video(video_url):
    audio_path, video_title = download_audio(video_url)

    print("\n🎥 Available Whisper models:")
    print("tiny | base | small | medium | large")
    model_name = input("Enter model name: ").strip().lower()

    if model_name not in ['tiny', 'base', 'small', 'medium', 'large']:
        print("⚠️ Invalid model name. Using 'base' model by default.")
        model_name = 'base'

    force_lang = input("\n🌐 Force transcription in English? (yes/no): ").strip().lower()
    if force_lang == "yes":
        segments, language_detected = transcribe_audio(audio_path, model_name, force_language="en")
    else:
        segments, language_detected = transcribe_audio(audio_path, model_name)

    print("\n🔍 Transcription preview:")
    for seg in segments:
        print(f"{seg['start']}s - {seg['text']}")

    print("\n💬 Available language codes (examples):")
    print("'en' (English), 'hi' (Hindi), 'fr' (French), 'ja' (Japanese), etc.")
    target_lang_code = input("Enter target language code (or press Enter to skip translation): ").strip().lower()

    translation_enabled = False
    translated_segments = None

    if target_lang_code and target_lang_code != "en":
        translation_enabled = True
        translated_segments = translate_segments(segments, target_lang_code)

    save_to_pdf(segments, translated_segments, video_title, translation_enabled)
    cleanup(audio_path)

    print("\n🔍 Final Transcription Preview:")
    for seg in segments:
        print(f"{seg['start']}s: {seg['text']}")

# Entry point
if __name__ == "__main__":
    print("🎬 YouTube to Transcript & Translation PDF Generator")
    print("----------------------------------------------------")
    url = input("\n🔗 Enter YouTube video URL: ").strip()
    if url:
        process_video(url)
    else:
        print("❌ No URL entered. Exiting.")
