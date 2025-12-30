# Security Policy

Deepgram's security policy can be found on our main website.

[Deepgram Security Policy](https://developers.deepgram.com/documentation/security/security-policy/)

## Supply Chain Security

This project implements security best practices to protect against vulnerabilities in dependencies.

### Python Dependency Management

**Backend Security:**
- All Python dependencies are pinned to exact versions in `requirements.txt`
- No version ranges allowed (e.g., `>=`, `~=`)
- Dependencies should be updated intentionally and tested thoroughly

**Best Practices:**
```bash
# Install from pinned versions
pip install -r requirements.txt

# Use virtual environments to isolate dependencies
python -m venv env
source env/bin/activate
```

### Frontend Security

The frontend uses pnpm for package management (consistent with all Deepgram starters):

**Frontend Dependencies:**
- Managed via `frontend/package.json`
- Built with Vite for optimized, secure static files
- Served as pre-built assets from `frontend/dist/`

**Frontend Build:**
```bash
cd frontend
pnpm install
pnpm run build
```

### API Key Security

**Critical: Never commit API keys to version control**

- Store API keys in `.env` files (excluded from git)
- Use environment variables for all sensitive configuration
- `.env` file should contain:
  ```
  DEEPGRAM_API_KEY=your_api_key_here
  ```
- Get your API key from: https://console.deepgram.com

### Security Scanning

For security vulnerability scanning, consider:

**Python Dependencies:**
```bash
# Using Snyk (if installed)
snyk test --file=requirements.txt

# Or use pip-audit
pip install pip-audit
pip-audit
```

**Frontend Dependencies:**
```bash
cd frontend
pnpm audit
# or
snyk test
```

### Dependency Update Strategy

When updating dependencies:
1. Update one dependency at a time when possible
2. Test the application thoroughly after each update
3. Review dependency changelogs for breaking changes
4. Pin the new version exactly in `requirements.txt`
5. Commit the updated `requirements.txt`

### Virtual Environment Best Practices

Always use virtual environments to:
- Isolate project dependencies
- Prevent system-wide package conflicts
- Ensure reproducible builds

```bash
# Create virtual environment
python -m venv env

# Activate
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Deactivate when done
deactivate
```

### Production Deployment

For production deployments:
- Use environment variables for all configuration
- Never expose `.env` files
- Use HTTPS for all API communications
- Set appropriate CORS policies (restrict origins in production)
- Keep dependencies up to date with security patches

### Reporting Security Issues

If you discover a security vulnerability in this project:

1. **Do NOT** open a public GitHub issue
2. Email security concerns to: security@deepgram.com
3. Include detailed information about the vulnerability
4. Allow reasonable time for response before public disclosure

We take security seriously and will respond promptly to legitimate security concerns.

### Additional Resources

- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Deepgram Security Documentation](https://developers.deepgram.com/documentation/security/)
