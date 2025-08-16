# FFmpeg Layer for AWS Lambda

This directory contains the FFmpeg static binary for AWS Lambda.

## Setup Instructions

1. Download FFmpeg static binary for Amazon Linux 2:
   ```bash
   cd layers/ffmpeg/bin
   wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
   tar xf ffmpeg-release-amd64-static.tar.xz
   cp ffmpeg-*-amd64-static/ffmpeg .
   cp ffmpeg-*-amd64-static/ffprobe .
   chmod +x ffmpeg ffprobe
   rm -rf ffmpeg-*-amd64-static*
   ```

2. Verify structure:
   ```
   layers/ffmpeg/
   ├── bin/
   │   ├── ffmpeg    # Main binary
   │   └── ffprobe   # Probe binary
   └── README.md
   ```

## Usage in Lambda

The binaries will be available at `/opt/bin/ffmpeg` and `/opt/bin/ffprobe` in your Lambda function.

Update your PATH in the Lambda handler:
```python
import os
os.environ['PATH'] = '/opt/bin:' + os.environ.get('PATH', '')
```