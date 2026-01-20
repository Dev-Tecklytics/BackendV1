# Re-export get_current_user from deps for backward compatibility
from app.core.deps import get_current_user, oauth2_scheme

__all__ = ['get_current_user', 'oauth2_scheme']
