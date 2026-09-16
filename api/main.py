# Deprecated: pylogs_hook is a local-only dev tool, not shipped in production.
# This file is kept for backward compatibility with local development setups.
# In production, use app.main:app directly (see Dockerfile).
try:
    from pylogs_hook import patch

    patch()
except ImportError:
    pass
