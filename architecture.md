# Auto Daddy - Software Architecture

## Overview
Auto Daddy is a desktop application for generating ASMR daddy audio content using Google's Gemini 2.5 for text generation and multi-speaker API for audio synthesis. The application allows users to either manually input scripts or have the AI generate them, with customization options for script length.

## Modules

### 1. User Interface Module (PyQt)
- Main application window
- Script input area (manual entry)
- AI generation controls
  - Script length selector
  - Theme/topic input
  - Generate button
- Voice selection dropdown
- Audio playback controls
- Save options

### 2. Text Generation Module
- Gemini 2.5 API integration
- Prompt engineering for ASMR daddy content
- Script length control
- Error handling and retry logic

### 3. Audio Synthesis Module
- Multi-speaker API integration
- Voice configuration
- Audio format handling
- WAV file generation

### 4. File Management Module
- Save generated scripts
- Save audio files
- Load previous scripts

## Data Flow
1. User inputs parameters (script length, theme) or manual script
2. If AI generation selected:
   - Text Generation Module creates script using Gemini 2.5
   - Generated script displayed in UI for review/editing
3. User selects voice options
4. Audio Synthesis Module converts script to audio
5. Audio is played through UI and/or saved to file

## Dependencies
- Python 3.8+
- PyQt5
- Google Gemini API client
- Audio processing libraries

## Configuration
- API key management
- Default voice settings
- Output directory settings
