# Complex Authentication System Implementation

## Mission Objective
Implement a complete user authentication system for a web application that feels "like a trusted friend helping you back through the door you forgot the key to" rather than a bureaucratic security checkpoint.

## Emotional Context
Users often feel abandoned and frustrated when they lose access to their accounts. The authentication flow should make users feel cared for and supported, not interrogated and suspicious.

## Technical Requirements

### Core Components Needed:
1. **Multi-factor authentication** with email, SMS, and authenticator app options
2. **Password reset flow** that guides users through recovery like a patient friend
3. **Account lockout protection** with progressive delays and helpful messaging
4. **Session management** with secure tokens and automatic cleanup
5. **Admin dashboard** for managing user accounts and security settings
6. **Audit logging** for security events and user activity

### Architecture Constraints:
- Use FastAPI for the backend
- React/TypeScript for the frontend
- PostgreSQL for data storage
- Redis for session storage and rate limiting
- JWT tokens with refresh token rotation
- Follow the existing codebase patterns from Nexus knowledge
- Include comprehensive error handling and user-friendly messages
- Implement rate limiting to prevent abuse
- Add security headers and CSRF protection

### User Experience Goals:
- Password reset should feel supportive, not accusatory
- Multi-factor prompts should explain why it's needed
- Error messages should guide users toward solutions
- Loading states should show progress and build anticipation
- Success states should celebrate the user's accomplishment

### Security Requirements:
- Argon2 password hashing
- Secure random token generation
- HTTPS-only cookies
- Rate limiting on all auth endpoints
- Account lockout after failed attempts
- Audit logging for all security events
- GDPR-compliant data handling

## Implementation Notes:
- The system should integrate with the existing Nexus knowledge base
- Use Weaver for cohesive code generation across frontend/backend
- YOLO Protocol should autonomously execute the implementation
- Follow Prime Directives from the codebase history
- Include comprehensive testing and documentation

## Success Criteria:
- All authentication flows work end-to-end
- Security audit passes without critical issues
- User testing shows positive emotional response
- Code follows established patterns and conventions
- System integrates seamlessly with existing architecture