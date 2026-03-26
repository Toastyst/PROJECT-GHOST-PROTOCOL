"""
Mock LLM utilities for testing Ghost Protocol without API keys.
"""

import json
import re
from typing import Dict, Any, Optional


class MockLLM:
    """Mock LLM responses for testing Ghost Protocol components."""

    def __init__(self):
        self.response_templates = {
            'weaver_generation': {
                'pattern': r'generate.*code|create.*function|implement.*class',
                'response': '''```python
def authenticate_user(email: str, password: str) -> AuthResult:
    """Authenticate user with emotional support messaging."""
    try:
        # Validate input with helpful error messages
        if not email or '@' not in email:
            return AuthResult(
                success=False,
                message="I see you're having trouble with your email. Let me help you remember - it's usually your username followed by @ and your email provider.",
                user_id=None
            )

        if not password:
            return AuthResult(
                success=False,
                message="Your password field looks empty. I'm here to help you get back in - would you like me to guide you through the password reset process?",
                user_id=None
            )

        # Check against database with progressive delays for security
        user = get_user_by_email(email)
        if not user:
            return AuthResult(
                success=False,
                message="I don't see that email in our system. If you're new here, I'd be happy to help you create an account instead.",
                user_id=None
            )

        # Verify password with argon2
        if verify_password(password, user.hashed_password):
            # Log successful authentication
            log_auth_event(user.id, 'login_success')

            return AuthResult(
                success=True,
                message=f"Welcome back! It's good to see you again.",
                user_id=user.id
            )
        else:
            # Progressive delay for failed attempts
            failed_attempts = get_failed_attempts(email)
            delay = min(failed_attempts * 2, 30)  # Max 30 seconds

            if failed_attempts >= 5:
                lock_account_temporarily(email, duration=900)  # 15 minutes
                return AuthResult(
                    success=False,
                    message="I've noticed several attempts. For your security, I'm going to pause login attempts for 15 minutes. This gives us both time to make sure everything is safe.",
                    user_id=None
                )

            return AuthResult(
                success=False,
                message=f"The password doesn't match what I have on file. You've had {failed_attempts} attempts. I care about your security - would you like help with password reset?",
                user_id=None
            )

    except Exception as e:
        # Comprehensive error handling
        log_error('authentication_error', str(e))
        return AuthResult(
            success=False,
            message="I'm experiencing some technical difficulties right now. Please try again in a moment, or contact support if this continues.",
            user_id=None
        )
```'''
            },

            'nexus_query': {
                'pattern': r'query.*knowledge|search.*patterns|find.*examples',
                'response': '''Based on the codebase patterns I've learned:

**Authentication Patterns:**
- Use Argon2 for password hashing (security + emotional trust)
- Progressive delays on failed attempts (security without punishment)
- Supportive error messages (emotional UX)
- JWT with refresh token rotation (secure sessions)
- Rate limiting on auth endpoints (protection without blocking)

**Emotional UX Patterns:**
- Error messages that guide toward solutions
- Loading states that build anticipation
- Success messages that celebrate accomplishment
- Progressive disclosure of information
- Supportive language throughout flows

**Security Patterns:**
- Account lockout with helpful messaging
- Audit logging for all security events
- CSRF protection on state-changing operations
- HTTPS-only cookies with secure flags
- Input validation with descriptive errors

**Database Patterns:**
- User table with email, hashed_password, failed_attempts, locked_until
- Session table with user_id, token, expires_at, ip_address
- Audit log table for security events
- Rate limit table for endpoint protection'''
            },

            'yolo_planning': {
                'pattern': r'plan.*mission|create.*strategy|design.*approach',
                'response': '''**MISSION PLAN: Supportive Authentication System**

**Emotional Foundation:**
This system will feel like a trusted friend helping you through a difficult moment, not a security guard interrogating you.

**Phased Approach:**

1. **Foundation Phase** - Database schema and core models
   - User model with progressive security fields
   - Session management with emotional metadata
   - Audit logging for trust building

2. **Backend Phase** - FastAPI authentication service
   - Supportive login endpoint with progressive delays
   - Password reset flow that feels like guidance
   - Multi-factor auth that explains "why" it matters

3. **Frontend Phase** - React emotional UX
   - Loading states that show care and progress
   - Error messages that guide toward solutions
   - Success celebrations that acknowledge effort

4. **Integration Phase** - End-to-end emotional flow
   - Seamless transitions between states
   - Consistent supportive messaging
   - Progressive disclosure of security measures

**Success Metrics:**
- Users feel supported during authentication
- Security measures feel protective, not punitive
- Error recovery feels guided, not blocked
- Success moments feel celebrated

**Risk Mitigation:**
- Extensive testing of emotional flows
- Security audit before deployment
- User feedback on emotional experience
- Gradual rollout with monitoring'''
            },

            'security_review': {
                'pattern': r'review.*security|audit.*code|check.*vulnerabilities',
                'response': '''**Security Audit Results:**

✅ **PASSED:**
- Argon2 password hashing implementation
- JWT token rotation with secure storage
- Rate limiting on authentication endpoints
- Account lockout with progressive delays
- HTTPS-only cookies with secure flags
- CSRF protection on state-changing operations
- Input validation with sanitization
- Audit logging for security events
- Secure random token generation
- No hardcoded secrets in codebase

⚠️ **ATTENTION NEEDED:**
- Consider implementing password strength requirements with supportive messaging
- Add session invalidation on suspicious activity
- Implement geo-blocking for unusual login locations (with user notification)
- Consider adding device fingerprinting for additional security

**Emotional Security Score: 8.5/10**
The security measures feel protective rather than punitive, which builds user trust while maintaining safety.'''
            },

            'default': {
                'response': '''I understand your request. Based on the Ghost Protocol's knowledge and emotional intelligence, here's my response:

The system is designed to feel supportive and understanding, helping users through authentication challenges rather than creating barriers. Every interaction should build trust and provide guidance toward successful completion.

Key principles:
- Supportive error messages that guide solutions
- Progressive security measures that feel protective
- Emotional validation of user efforts
- Clear communication of security reasoning
- Celebration of successful authentication

Would you like me to elaborate on any specific aspect of this approach?'''
            }
        }

    def generate_with_reasoning(self, prompt: str) -> str:
        """Generate mock response based on prompt content."""
        prompt_lower = prompt.lower()

        # Find matching template
        for template_name, template_data in self.response_templates.items():
            if template_name == 'default':
                continue

            pattern = template_data['pattern']
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                return template_data['response']

        # Return default response
        return self.response_templates['default']['response']

    def generate_code(self, task: str, prompt: str) -> str:
        """Generate code with mock LLM."""
        return self.generate_with_reasoning(prompt)


# Global mock instance
_mock_llm = None

def get_mock_llm() -> MockLLM:
    """Get mock LLM instance for testing."""
    global _mock_llm
    if _mock_llm is None:
        _mock_llm = MockLLM()
    return _mock_llm