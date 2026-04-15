from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from templates_config import render
from database import get_db_connection
from dependencies import get_current_user

router = APIRouter()

@router.get('/dashboard', response_class=HTMLResponse)
async def dashboard(request: Request, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM accounts WHERE user_id=%s", (user['user_id'],))
    accounts = cur.fetchall()
    cur.close()
    conn.close()
    return render(request, 'dashboard.html', name=user['name'], accounts=accounts)
