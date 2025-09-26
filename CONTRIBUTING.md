# Contributing to Bongo Cat Monitor Remix

## Local Development Setup

### Keep the Repository Clean

- **Use a virtual environment for Python**:
  ```bash
  python -m venv .venv && source .venv/bin/activate  # macOS/Linux
  # Windows: python -m venv .venv && .venv\Scripts\activate
  ```

- **Install Node.js dependencies** with `npm ci` (or `pnpm i --frozen-lockfile`) — but **do not commit** `node_modules/`.

- **Build/cached paths are ignored** via `.gitignore`:
  - `node_modules/` - Node.js dependencies
  - `__pycache__/` - Python bytecode cache
  - `dist/`, `build/` - Build artifacts
  - `.venv/`, `venv/` - Virtual environments
  - `.DS_Store` - macOS system files
  - `.arduino-build/`, `.pio/` - Firmware build caches

- **If you accidentally track these files**, untrack them (they'll stay on your disk):
  ```bash
  git rm -r --cached node_modules dist build __pycache__
  ```

- **Before pushing**, always run `git status` — it should be clean of build or cache files.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test thoroughly
5. Ensure `git status` is clean
6. Commit with conventional commit messages
7. Push and create a pull request

### Commit Message Format

Use conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Testing changes
- `chore:` - Maintenance tasks

Example: `feat: add hardware temperature monitoring`

### Testing

- Test on multiple platforms when possible (Windows, macOS, Linux)
- Verify builds work correctly
- Check that `git status` remains clean after builds
- Test both Python app and Electron wrapper

### Pull Request Guidelines

- Provide a clear description of changes
- Reference any related issues
- Ensure CI checks pass
- Request review from maintainers

## Repository Hygiene

This repository uses automated hygiene checks to prevent accidental commits of build artifacts, dependencies, and cache files. The hygiene guard will fail if banned paths are added to commits.

**Banned paths include:**
- `node_modules/`
- `__pycache__/`
- `.DS_Store`
- `dist/`, `build/`
- `.venv/`, `venv/`
- `.arduino-build/`, `.pio/`

If you need to clean up accidentally tracked files, use:
```bash
git rm -r --cached <banned-path>
```