from fastapi import APIRouter, Request, Form, Response, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from templates_config import render
from database import get_db_connection
from services.auth_service import create_access_token
import re
import psycopg2
from pydantic import ValidationError
from schemas import UserRegister, PasswordUpdate
from dependencies import get_current_user

router = APIRouter()

@router.get('/', response_class=HTMLResponse)
async def login_get(request: Request):
    return render(request, 'login.html')

@router.post('/', response_class=HTMLResponse)
async def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    email = email.strip().lower()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user:
        return render(request, 'message.html', msg=" Account does not exist. Please register first.")
    elif user['password'] != password:
        return render(request, 'message.html', msg=" Incorrect password. Please try again.")
    else:
        # Success - create JWT
        token = create_access_token(data={"user_id": user['user_id'], "name": user['name']})
        response = RedirectResponse(url='/dashboard', status_code=303)
        response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
        return response

@router.get('/register', response_class=HTMLResponse)
async def register_get(request: Request):
    return render(request, 'register.html', error=None)

@router.post('/register', response_class=HTMLResponse)
async def register_post(
    request: Request, 
    name: str = Form(...), 
    email: str = Form(...), 
    password: str = Form(...)
):
    error = None
    name = name.strip()
    email = email.strip().lower()

    try:
        UserRegister(name=name, email=email, password=password)
    except ValidationError as e:
        err = e.errors()[0]
        if 'email' in err['loc']:
            error = "Invalid email format! Please enter a valid email."
        elif 'password' in err['loc']:
            error = err['msg']
        else:
            error = err['msg']
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", 
                        (name, email, password))
            conn.commit()
            return render(request, 'message.html', msg=" Registration Successful! Please log in.")
        except psycopg2.IntegrityError:
            conn.rollback()
            error = "This email is already registered."
        except Exception as e:
            conn.rollback()
            print(" Postgres Error:", e)
            error = "Unexpected database error. Please try again."
        finally:
            cur.close()
            conn.close()

    return render(request, 'register.html', error=error)

@router.get('/logout')
async def logout(request: Request):
    response = RedirectResponse(url='/', status_code=303)
    response.delete_cookie("access_token")
    return response

@router.get('/update-password', response_class=HTMLResponse)
async def update_password_get(request: Request, user: dict = Depends(get_current_user)):
    return render(request, 'update_password.html')

@router.patch('/update-password')
async def update_password(payload: PasswordUpdate, user: dict = Depends(get_current_user)):
    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password and confirm password do not match.")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT password FROM users WHERE user_id = %s", (user['user_id'],))
        db_user = cur.fetchone()

        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        if db_user['password'] != payload.old_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password.")

        if payload.old_password == payload.new_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be different from old password.")

        cur.execute("UPDATE users SET password = %s WHERE user_id = %s", (payload.new_password, user['user_id']))
        conn.commit()

        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Password updated successfully."})
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Database error during password update: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while updating the password.")
    finally:
        cur.close()
        conn.close()
