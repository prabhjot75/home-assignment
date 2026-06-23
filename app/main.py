from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.database import Base, engine


# Build local table relations safely on bootup execution
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bookmarks API",
    version="1.1.0",
    docs_url="/api/docs",  # Expose interactive openapi docs interface here 
    redoc_url=None
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_err = errors[0] if errors else {}
    field = ".".join([str(p) for p in first_err.get("loc", []) if p != "body"])
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",  # Conforms exactly to required error envelope 
                "message": f"Validation failure on: {first_err.get('msg')}", 
                "details": {
                    "field": field or "payload", 
                    "constraint": first_err.get("type", "value_error").upper().replace(".", "_") 
                }
            }
        }
    )