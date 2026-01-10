from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import planejamento as planejamento_module

app = FastAPI()

# Allow frontend dev server origins (Vite default 5173) and localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers defined under app.routes
app.include_router(planejamento_module.router)
