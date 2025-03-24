# kalturee

This repository contains a collection of scripts for interacting with Kaltura's APIs, designed to streamline workflows for creating demos, uploading content, and managing media assets on the Kaltura platform.

Uses https://github.com/yt-dlp/yt-dlp for downloading videos from YouTube

## Features

As of 2025-03-24, the following features are available:

- **YouTube Video Downloads**: Automated downloading of YouTube videos for demo purposes
- **Kaltura Video Upload**: Direct upload of videos to Kaltura with automatic:
  - Thumbnail generation from the first frame
  - Caption generation (using WhisperX)
  - AI-generated title & description based on video content
- **PowerPoint Upload**: Direct upload of PowerPoint presentations to Kaltura with automatic:
  - Thumbnail generation from the first slide
  - Title extraction from filename
  - AI-generated descriptions based on slide content

## Requirements

- Python 3.6+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube video downloads
- Kaltura API credentials (stored in `.env` file)
- LibreOffice (for PowerPoint slide conversion)
- Ollama (for AI-generated descriptions)

## Setup

1. Clone this repository
2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Kaltura credentials:
   ```
   user_secret=your_user_secret
   admin_secret=your_admin_secret
   partner_id=your_partner_id
   ```


