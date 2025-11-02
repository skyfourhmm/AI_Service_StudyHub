from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import topic_test, custom_test, grader_router

app = FastAPI(title="AI English Test Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký router
app.include_router(topic_test.router)
app.include_router(custom_test.router)
app.include_router(grader_router.router)

@app.get("/")
async def root():
    return {"message": "AI English Test API is running 🚀"}
