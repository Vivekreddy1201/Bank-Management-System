from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from templates_config import render
from database import get_db_connection
from dependencies import get_current_user

router = APIRouter()

@router.get('/create_account', response_class=HTMLResponse)
async def create_account_get(request: Request, user: dict = Depends(get_current_user)):
    return render(request, 'create_account.html')

@router.post('/create_account', response_class=HTMLResponse)
async def create_account_post(request: Request, type: str = Form(...), user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO accounts (user_id, type, balance) VALUES (%s, %s, 0)",
        (user['user_id'], type.capitalize())
    )
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse(url='/dashboard', status_code=303)

@router.get('/deposit', response_class=HTMLResponse)
async def deposit_get(request: Request, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT account_id, account_no, type, balance FROM accounts WHERE user_id=%s", (user['user_id'],))
    accounts = cur.fetchall()
    cur.close()
    conn.close()
    return render(request, 'deposit.html', accounts=accounts)

@router.post('/deposit', response_class=HTMLResponse)
async def deposit_post(
    request: Request,
    acc_id: str = Form(...),
    amount: float = Form(...),
    user: dict = Depends(get_current_user)
):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT account_no FROM accounts WHERE account_id=%s AND user_id=%s", (acc_id, user['user_id']))
    acc = cur.fetchone()
    if not acc:
        msg = "You can only deposit into your own accounts!"
    else:
        try:
            cur.execute("CALL deposit(%s, %s)", (acc_id, amount))
            conn.commit()
            msg = f"₹{amount:.2f} deposited successfully into Account {acc['account_no']}."
        except Exception as e:
            msg = f"Error: {e}"
    cur.close()
    conn.close()
    return render(request, 'message.html', msg=msg)

@router.get('/withdraw', response_class=HTMLResponse)
async def withdraw_get(request: Request, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT account_id, account_no, type, balance FROM accounts WHERE user_id=%s", (user['user_id'],))
    accounts = cur.fetchall()
    cur.close()
    conn.close()
    return render(request, 'withdraw.html', accounts=accounts)

@router.post('/withdraw', response_class=HTMLResponse)
async def withdraw_post(
    request: Request,
    acc_id: str = Form(...),
    amount: float = Form(...),
    user: dict = Depends(get_current_user)
):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT account_no FROM accounts WHERE account_id=%s AND user_id=%s", (acc_id, user['user_id']))
    acc = cur.fetchone()
    if not acc:
        msg = "You can only withdraw from your own accounts!"
    else:
        try:
            cur.execute("CALL withdraw(%s, %s)", (acc_id, amount))
            conn.commit()
            msg = f"₹{amount:.2f} withdrawn successfully from Account {acc['account_no']}."
        except Exception as e:
            msg = f"Error: {e}"
    cur.close()
    conn.close()
    return render(request, 'message.html', msg=msg)

@router.get('/transfer', response_class=HTMLResponse)
async def transfer_get(request: Request, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT account_id, account_no, type, balance FROM accounts WHERE user_id=%s", (user['user_id'],))
    user_accounts = cur.fetchall()
    cur.close()
    conn.close()
    return render(request, 'transfer.html', accounts=user_accounts)

@router.post('/transfer', response_class=HTMLResponse)
async def transfer_post(
    request: Request,
    from_acc: str = Form(...),
    to_acc: str = Form(...),
    amount: float = Form(...),
    user: dict = Depends(get_current_user)
):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT account_id FROM accounts WHERE account_no=%s AND user_id=%s", (from_acc, user['user_id']))
    src = cur.fetchone()
    if not src:
        msg = "You can only transfer from your own account!"
        cur.close()
        conn.close()
        return render(request, 'message.html', msg=msg)

    cur.execute("SELECT account_id FROM accounts WHERE account_no=%s", (to_acc,))
    dest = cur.fetchone()
    if not dest:
        msg = "Destination account number not found!"
        cur.close()
        conn.close()
        return render(request, 'message.html', msg=msg)

    if from_acc == to_acc:
        msg = "You cannot transfer to the same account!"
        cur.close()
        conn.close()
        return render(request, 'message.html', msg=msg)

    try:
        cur.execute("CALL transfer_money(%s, %s, %s)", (src['account_id'], dest['account_id'], amount))
        conn.commit()
        msg = f"₹{amount:.2f} transferred successfully from A/c {from_acc} to A/c {to_acc}."
    except Exception as e:
        conn.rollback()
        msg = f"Error during transfer: {e}"

    cur.close()
    conn.close()
    return render(request, 'message.html', msg=msg)

@router.get('/transactions/{acc_id}', response_class=HTMLResponse)
async def transactions(request: Request, acc_id: int, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT account_no FROM accounts WHERE account_id=%s AND user_id=%s", (acc_id, user['user_id']))
    acc = cur.fetchone()
    if not acc:
        cur.close()
        conn.close()
        return render(request, 'message.html', msg="You can only view your own accounts.")
        
    cur.execute("SELECT * FROM transactions WHERE account_id=%s ORDER BY timestamp DESC", (acc_id,))
    txns = cur.fetchall()
    cur.close()
    conn.close()
    return render(request, 'transactions.html', txns=txns, acc_no=acc['account_no'])

@router.get('/delete_account/{acc_id}', response_class=HTMLResponse)
async def delete_account_get(request: Request, acc_id: int, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT account_id, account_no, balance FROM accounts WHERE account_id=%s AND user_id=%s",
                (acc_id, user['user_id']))
    acc = cur.fetchone()
    cur.close()
    conn.close()

    if not acc:
        return render(request, 'message.html', msg="Account not found or unauthorized access!")
    return render(request, 'delete_account.html', acc=acc)

@router.get('/withdraw_balance/{acc_id}')
async def withdraw_balance(request: Request, acc_id: int, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT balance, account_no FROM accounts WHERE account_id=%s AND user_id=%s",
                (acc_id, user['user_id']))
    acc = cur.fetchone()

    if not acc:
        cur.close()
        conn.close()
        return render(request, 'message.html', msg="Account not found!")

    if acc['balance'] <= 0:
        cur.close()
        conn.close()
        return render(request, 'message.html', msg="No funds available to withdraw.")

    try:
        cur.execute("CALL withdraw(%s, %s)", (acc_id, acc['balance']))
        conn.commit()
        cur.close()
        conn.close()
        return RedirectResponse(url=f"/confirm_delete/{acc_id}", status_code=303)
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return render(request, 'message.html', msg=f"Error: {e}")

@router.get('/transfer_balance/{acc_id}', response_class=HTMLResponse)
async def transfer_balance_get(request: Request, acc_id: int, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT account_no, balance FROM accounts WHERE account_id=%s AND user_id=%s",
                (acc_id, user['user_id']))
    acc = cur.fetchone()
    cur.execute("SELECT account_id, account_no FROM accounts WHERE user_id=%s AND account_id!=%s",
                (user['user_id'], acc_id))
    other_accs = cur.fetchall()
    cur.close()
    conn.close()

    if not acc:
        return render(request, 'message.html', msg="Account not found!")
    return render(request, 'transfer_balance.html', acc=acc, other_accs=other_accs)

@router.post('/transfer_balance/{acc_id}', response_class=HTMLResponse)
async def transfer_balance_post(request: Request, acc_id: int, to_acc: str = Form(...), user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT account_no, balance FROM accounts WHERE account_id=%s AND user_id=%s",
                (acc_id, user['user_id']))
    acc = cur.fetchone()

    if not acc:
        cur.close()
        conn.close()
        return render(request, 'message.html', msg="Account not found!")

    amount = acc['balance']
    cur.execute("SELECT account_id FROM accounts WHERE account_no=%s AND user_id=%s",
                (to_acc, user['user_id']))
    dest = cur.fetchone()

    if not dest:
        cur.close()
        conn.close()
        return render(request, 'message.html', msg="Invalid destination account!")

    try:
        cur.execute("CALL transfer_money(%s, %s, %s)", (acc_id, dest['account_id'], amount))
        conn.commit()
        cur.close()
        conn.close()
        return RedirectResponse(url=f"/confirm_delete/{acc_id}", status_code=303)
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return render(request, 'message.html', msg=f"Error: {e}")

@router.get('/confirm_delete/{acc_id}', response_class=HTMLResponse)
async def confirm_delete_get(request: Request, acc_id: int, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT account_id, account_no, balance FROM accounts WHERE account_id=%s AND user_id=%s",
                (acc_id, user['user_id']))
    acc = cur.fetchone()
    cur.close()
    conn.close()

    if not acc:
        return render(request, 'message.html', msg="Account not found or unauthorized access!")
    return render(request, 'confirm_delete.html', acc=acc)

@router.post('/delete_confirmed/{acc_id}', response_class=HTMLResponse)
async def delete_confirmed_post(request: Request, acc_id: int, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT account_no, balance FROM accounts WHERE account_id=%s AND user_id=%s",
                (acc_id, user['user_id']))
    acc = cur.fetchone()

    if not acc:
        msg = "Account not found!"
    elif acc['balance'] > 0:
        msg = f"Account {acc['account_no']} still has ₹{acc['balance']:.2f}. Withdraw or transfer before deleting."
    else:
        cur.execute("DELETE FROM accounts WHERE account_id=%s AND user_id=%s", (acc_id, user['user_id']))
        conn.commit()
        msg = f"Account {acc['account_no']} deleted successfully."

    cur.close()
    conn.close()
    return render(request, 'message.html', msg=msg)
