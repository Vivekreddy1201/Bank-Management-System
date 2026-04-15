from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from services.auth_service import verify_access_token

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        # User not logged in, throw HTTPException error
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/"})
    
    # We prefix token with 'Bearer '
    if token.startswith("Bearer "):
        token = token.split(" ")[1]
        
    payload = verify_access_token(token)
    if not payload:
        # Token expired or invalid
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/"})
        
    return payload

def get_current_user_optional(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    if token.startswith("Bearer "):
        token = token.split(" ")[1]
    return verify_access_token(token)
