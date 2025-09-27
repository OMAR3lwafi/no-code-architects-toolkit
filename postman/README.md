# Postman API Collection

This directory contains the Postman collection and environment files for the No-Code Architects Toolkit API.

## Files

- `NCA-Toolkit.postman_collection.json` - The main API collection with all endpoints
- `NCA-Toolkit.postman_environment.json` - Environment variables for the API

## How to Import

1. Open Postman
2. Click "Import" button
3. Select both JSON files
4. The collection and environment will be imported

## How to Export from Postman

1. **Export Collection:**
   - Click the three dots (...) next to collection name
   - Select "Export"
   - Choose "Collection v2.1"
   - Save as `NCA-Toolkit.postman_collection.json`

2. **Export Environment:**
   - Go to Environments tab
   - Click three dots next to environment
   - Select "Export"
   - Save as `NCA-Toolkit.postman_environment.json`

## Environment Variables

Make sure to configure these variables in your environment:
- `base_url` - Your API URL (e.g., http://localhost:8080)
- `x-api-key` - Your API key

## Available Endpoints

The collection includes all API endpoints documented in the main README:
- Audio operations
- Video operations
- Media transcription
- S3 upload
- Toolkit utilities
- And more...