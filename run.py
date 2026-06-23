# This automatically launches your browser

import uvicorn
import asyncio
from app.database import Base, engine

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main():
    await init_db()
    config = uvicorn.Config(app="app.main:app", host="127.0.0.1", port=9500, reload=True, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())