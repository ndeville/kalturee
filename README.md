# kalturee

This repository contains a collection of scripts for interacting with Kaltura's APIs, designed to streamline workflows for creating demos, uploading content, and managing media assets on the Kaltura platform.

> WORK IN PROGRESS

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
- **Download Website Resources**: Download favicons only for now. TODO: download stylesheet (to extract fonts & colors)
- **Download Website Images**: Download HD images from a target website (for banners in demos)
- **Loop Video**: Loop a video to a specific duration
- **Download YouTube Channel Metadata**: Download metadata for a YouTube channel
- **Download YouTube Videos**: Download videos from a YouTube channel
- **Download YouTube Captions**: Download captions from a YouTube video

## Requirements

- Python 3.6+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube video downloads
- Kaltura API credentials (stored in `.env` file)
- LibreOffice (for PowerPoint slide conversion)
- Ollama (for AI-generated descriptions)



