# Contributing to TrailBird AI

Thank you for your interest in contributing to **TrailBird AI**! We welcome contributions from developers, ornithologists, hikers, and naturalists of all skill levels.

## How to Contribute

1. **Fork & Clone the Repository**:
   ```bash
   git clone https://github.com/satanic47/trailbird-ai.git
   cd trailbird-ai
   ```
2. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Local Testing & Verification**:
   - Web application: Run `python -m http.server 8000` and test offline features in browser.
   - Python CLI: Run `python trailbird.py audio_samples/american_robin.wav`.
4. **Submit a Pull Request (PR)**:
   - Ensure your code follows clean formatting standards.
   - Describe the changes made and any relevant issue numbers.

## Ground Rules for Collaborators

- Respect the [Code of Conduct](CODE_OF_CONDUCT.md).
- Keep all local AI inference offline-first (zero network requests in client JS runtime).
- Tag maintainers in PR reviews for fast approval.
