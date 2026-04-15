from fastapi import Request
from fastapi.templating import Jinja2Templates
from dependencies import get_current_user_optional

templates = Jinja2Templates(directory="frontend")

def render(request: Request, template_name: str, **kwargs):
    context = {"request": request}
    
    # Emulate the 'session' context for templates that expect session.name
    user = get_current_user_optional(request)
    if user:
        context["session"] = user
    else:
        context["session"] = {}
        
    context.update(kwargs)
    return templates.TemplateResponse(template_name, context)
