import bcrypt
import logging

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    Bcrypt has a 72-byte limit, so we truncate the password if necessary.
    """
    try:
        # Properly truncate password to ensure it's <= 72 bytes when UTF-8 encoded
        # This handles multi-byte UTF-8 characters correctly
        truncated_password = password
        while len(truncated_password.encode('utf-8')) > 72:
            truncated_password = truncated_password[:-1]
        
        if len(truncated_password) < len(password):
            logger.info(f"Password truncated: {len(password)} chars -> {len(truncated_password)} chars ({len(truncated_password.encode('utf-8'))} bytes)")
        
        # Convert password to bytes and hash it
        password_bytes = truncated_password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        logger.info("Password hashed successfully")
        # Return as string for database storage
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    Truncates the plain password to match the hashing behavior.
    """
    try:
        # Use the same truncation logic as hash_password
        truncated_password = plain_password
        while len(truncated_password.encode('utf-8')) > 72:
            truncated_password = truncated_password[:-1]
        
        # Convert to bytes for bcrypt
        password_bytes = truncated_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False

