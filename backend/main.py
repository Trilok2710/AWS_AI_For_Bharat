from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.asha import auth, patients, cases

app = FastAPI(title="MediConnect AI")

# ----------------------------------------
# CORS Configuration (for frontend)
# ----------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------
# Include Routers
# ----------------------------------------

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(cases.router)


@app.get("/")
def root():
    return {"message": "MediConnect AI Backend Running"}