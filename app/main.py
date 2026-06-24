from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database import Base, engine
from app.models.auth import User
from app.models.bookmarks import Bookmark, Tag, bookmark_tags
from app.api.auth import router as auth_router
from app.api.bookmarks import router as bookmark_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Bookmarks Layered API Architecture",
    version="1.1.0",

    docs_url="/api/docs", # <--- Served explicitly at /api/docs
    redoc_url=None, # Disable secondary visualization layouts
    lifespan=lifespan
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_err = errors[0] if errors else {}
    
    loc_path = first_err.get("loc", [])
    field = ".".join([str(p) for p in loc_path if p != "body"]) or "payload"
    
    type_code = first_err.get("type", "value_error")
    constraint = type_code.upper().replace(".", "_")
    
    ctx = first_err.get("ctx", {})
    limit_val = ctx.get("limit") or ctx.get("expected")

    details = {
        "field": field,
        "constraint": constraint
    }
    if limit_val is not None:
        details["limit"] = limit_val

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": first_err.get("msg", "Input validation failed."),
                "details": details
            }
        }
    )
app.include_router(auth_router)
app.include_router(bookmark_router)