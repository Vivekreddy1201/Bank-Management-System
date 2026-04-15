from fastapi import FastAPI
import uvicorn

from routers import auth, dashboard, bank

app = FastAPI()


app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(bank.router)

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
