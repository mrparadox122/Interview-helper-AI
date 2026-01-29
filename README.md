# 🎧 AI Audio Assistant - Always On Top

A Python desktop application that hovers on top of all windows, captures system audio (speakers output), and uses Google's Gemini API to answer questions based on the audio content.

## ✨ Features

- **Always On Top**: Window stays above all other applications
- **System Audio Capture**: Records from speakers/system audio (not microphone)
- **Hold-to-Record**: Press and hold the "LISTEN" button to capture audio
- **Gemini AI Integration**: Processes audio through Google's Gemini API
- **Dark Theme UI**: Modern, easy-to-use interface
- **Audio Device Selection**: Choose from available audio input devices

## 📋 Prerequisites

1. **Python 3.8+** installed on your system
2. **Google Gemini API Key** (get it from [Google AI Studio](https://makersuite.google.com/app/apikey))
3. **System Audio Loopback** enabled (see setup instructions below)

## 🔧 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install sounddevice numpy soundfile google-generativeai
```

### 2. Enable System Audio Capture

The app needs to capture audio from your speakers. Here's how to enable it:

#### **Windows:**
1. Right-click the **Speaker icon** in the system tray
2. Select **"Sounds"** or **"Open Sound settings"**
3. Go to the **"Recording"** tab
4. Right-click in the empty space and enable **"Show Disabled Devices"**
5. You should see **"Stereo Mix"** or **"Wave Out Mix"** or **"What U Hear"**
6. Right-click it and select **"Enable"**
7. Set it as the **Default Recording Device** (or just enable it)

**Note**: If you don't see Stereo Mix, your audio driver might not support it. You can:
- Update your audio drivers
- Install [VB-Audio Virtual Cable](https://vb-audio.com/Cable/) (free virtual audio device)
- Use [VoiceMeeter](https://vb-audio.com/Voicemeeter/) (free audio mixer)

#### **macOS:**
1. Install [BlackHole](https://github.com/ExistentialAudio/BlackHole) (free virtual audio driver)
   ```bash
   brew install blackhole-2ch
   ```
2. Open **Audio MIDI Setup** (in Applications/Utilities)
3. Create a **Multi-Output Device** that includes both your speakers and BlackHole
4. Set BlackHole as your input device in the app

#### **Linux:**
Use PulseAudio or PipeWire loopback:
```bash
# PulseAudio
pactl load-module module-loopback

# Check available devices
pactl list sources short
```

### 3. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the API key

## 🚀 Usage

### Run the Application

```bash
python audio_ai_assistant.py
```

### Using the App

1. **Enter API Key**: 
   - Paste your Gemini API key in the top field
   - Click **"Save"** (it will be saved for future sessions)

2. **Select Audio Device**:
   - Choose your system audio device (Stereo Mix, BlackHole, etc.)
   - Click 🔄 to refresh the device list if needed

3. **Capture Audio**:
   - **Press and HOLD** the **"HOLD TO LISTEN"** button
   - Play audio from any source (YouTube, Spotify, video call, etc.)
   - **Release** the button when done
   - The app will process the audio and show the AI response

4. **View Response**:
   - The AI's answer will appear in the text area below
   - Click **"Clear"** to clear the response

5. **Toggle Always On Top**:
   - Click **"Toggle Always On Top"** to disable/enable the floating behavior

## 💡 Example Use Cases

- **YouTube Videos**: Ask questions about video content while watching
- **Online Meetings**: Get real-time summaries or answers during calls
- **Music**: Ask about song lyrics or music information
- **Podcasts**: Get clarifications or summaries of podcast content
- **Gaming**: Get help with game audio or voice chat
- **Language Learning**: Transcribe and translate foreign language audio

## 🎯 Tips

1. **Audio Quality**: Better audio quality = better AI responses
2. **Recording Duration**: Record 3-10 seconds for best results
3. **Clear Audio**: Reduce background noise for better accuracy
4. **Device Selection**: If no audio is captured, try a different device
5. **Volume Levels**: Ensure system audio is at a reasonable volume

## 🛠️ Troubleshooting

### "No input devices found"
- Enable Stereo Mix or install a virtual audio device (see setup section)
- Refresh the device list using the 🔄 button

### "Recording error" or No audio captured
- Check if the selected device is the correct one
- Ensure audio is actually playing when you hold the button
- Try increasing system volume
- On Windows, make sure Stereo Mix is not muted

### API Key errors
- Verify your API key is correct
- Check your internet connection
- Ensure you have API quota remaining at [Google Cloud Console](https://console.cloud.google.com/)

### Window not staying on top
- Click "Toggle Always On Top" button
- Some full-screen applications may override this

## 🔒 Privacy & Security

- Your API key is stored locally in `~/.audio_ai_config.json`
- Audio is temporarily saved locally and deleted after processing
- Audio is sent to Google's Gemini API for processing
- No audio is stored permanently by this application

## 📝 Notes

- The app captures **system audio output**, not your microphone
- Audio processing may take a few seconds depending on length
- Requires active internet connection for API calls
- Free Gemini API has rate limits (check Google's documentation)

## 🐛 Known Limitations

- Requires system audio loopback to be configured
- API calls count against your Gemini quota
- May not work with DRM-protected content
- Some applications may not allow audio capture

## 📄 License

This project is provided as-is for educational and personal use.

## 🤝 Contributing

Feel free to modify and improve the application for your needs!

---

**Happy Listening! 🎧✨**
