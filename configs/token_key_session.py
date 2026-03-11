"""Stub - local PostgreSQL-backed setup needs no real API tokens."""

class _NullTokens:
    def __getattr__(self, name):
        return None

all_token_key_session = _NullTokens()
