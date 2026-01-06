# Flask Transcription Starter

Speech-to-Text demo using Deepgram's API with Python Flask backend and web frontend.

## Prerequisites

- [Deepgram API Key](https://console.deepgram.com/signup?jump=keys) (sign up for free)
- Python 3.9+
- Node.js 14+ and pnpm (for frontend build)

## Quick Start

### 1. Install dependencies

**Backend (Python):**

```bash
pip install -r requirements.txt
```

**Frontend:**

```bash
cd frontend
pnpm install
pnpm run build
cd ..
```

### 2. Set your API key

Create a `.env` file:

```bash
DEEPGRAM_API_KEY=your_api_key_here
```

### 3. Run the app

**Production mode**:

```bash
flask run -p 3000
```

Open [http://localhost:3000](http://localhost:3000)

**Development mode with frontend HMR** (optional, for frontend development):

```bash
# Terminal 1: Backend
flask run -p 3000

# Terminal 2: Frontend dev server with instant reload
cd frontend && pnpm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Features

- Upload audio files or provide URLs for transcription
- Multiple model options
- View transcription history
- Responsive web interface

## How It Works

- **Backend** (`app.py`): Flask server implementing the `/stt/transcribe` endpoint per the STT API contract
- **Frontend** (`frontend/`): Vite-powered web UI built with Deepgram design system
- **API**: Integrates with [Deepgram's Speech-to-Text API](https://developers.deepgram.com/)

The frontend is built with Vite and served as static files from `frontend/dist/`. This ensures a consistent UI across all Deepgram starter apps regardless of backend language.


## Security

See [SECURITY.md](SECURITY.md) for security reporting procedures.

## Contributing

Contributions are welcome! Please review:
- [Contributing Guidelines](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)

## Getting Help

- [Open an issue](https://github.com/deepgram-starters/flask-transcription/issues)
- [Join our Discord](https://discord.gg/xWRaCDBtW4)
- [Deepgram Documentation](https://developers.deepgram.com/)

## License

MIT - See [LICENSE](./LICENSE)
