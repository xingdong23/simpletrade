from fastapi import APIRouter

# Test Router
test_router = APIRouter(prefix="/api/test", tags=["test"])

@test_router.get("/hello")
async def hello():
    return {"message": "Hello from SimpleTrade API!"}

@test_router.get("/info")
async def info():
    return {
        "status": "ok",
        "version": "0.1.0", # Consider making version dynamic later
        "api": "SimpleTrade API",
        "time": "2024-04-17" # Consider making time dynamic later
    }

# Health Check Router
health_router = APIRouter(prefix="/api/health", tags=["health"])

@health_router.get("/")
async def health_check():
    return {"status": "ok", "message": "API服务正常运行"}

# Combine routers for easier import in server.py (optional but can be convenient)
# You could import test_router and health_router separately in server.py,
# or import this combined router. Let's export them separately for clarity.

# Export individual routers
# router = APIRouter()
# router.include_router(test_router)
# router.include_router(health_router) 