from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from templates_config import render
from database import get_db_connection
from dependencies import get_current_user

router = APIRouter()

@router.get('/loans', response_class=HTMLResponse)
async def loans(request: Request, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT l.*, a.account_no 
        FROM loans l
        JOIN accounts a ON l.account_id = a.account_id
        WHERE l.user_id=%s
        ORDER BY l.start_date DESC
    """, (user['user_id'],))
    loans_list = cur.fetchall()
    cur.close()
    conn.close()
    return render(request, 'loans.html', loans=loans_list)

@router.get('/apply_loan', response_class=HTMLResponse)
async def apply_loan_get(request: Request, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT account_id, account_no FROM accounts WHERE user_id=%s", (user['user_id'],))
    accounts = cur.fetchall()
    cur.close()
    conn.close()
    return render(request, 'apply_loan.html', accounts=accounts)

@router.post('/apply_loan', response_class=HTMLResponse)
async def apply_loan_post(
    request: Request,
    account_id: str = Form(...),
    loan_type: str = Form(...),
    principal: str = Form(...),
    interest_rate: str = Form(...),
    user: dict = Depends(get_current_user)
):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO loans (user_id, account_id, loan_type, principal, interest_rate, start_date, end_date)
        VALUES (%s, %s, %s, %s, %s, CURRENT_DATE, CURRENT_DATE + INTERVAL '5 years')
    """, (user['user_id'], account_id, loan_type, principal, interest_rate))
    conn.commit()
    cur.close()
    conn.close()
    
    msg = f"Loan of ₹{principal} ({loan_type}) applied successfully!"
    return render(request, 'message.html', msg=msg)
