# GitHub Copilot Custom Instructions for TrailBird AI

When generating code or suggesting completions for the **TrailBird AI** repository, follow these domain guidelines:

## Code & Architecture Principles
- **Offline First**: All audio processing and Fast Fourier Transform (FFT) feature extraction must run 100% locally on device (Web Audio API in client JS / `wave` & `math` in Python CLI). Do not introduce external cloud API dependencies for inference.
- **Fast Fourier Transform (FFT)**: Keep audio analysis window size at 512 bins for sub-15ms local species matching latency.
- **UI & Accessibility**: Maintain clean Tailwind CSS responsive styling and support Touch Grass screen minimizer mode.

## Code Style
- **JavaScript**: Use modern ES6+ async/await, clean Web Audio API node connections, and local storage fallback handling.
- **Python**: Maintain standard library compatibility (`wave`, `math`, `sqlite3`, `datetime`). Use clear type annotations and UTF-8 terminal encoding.
