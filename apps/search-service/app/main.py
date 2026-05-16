from fastapi import FastAPI

from app.schemas.property import SearchRequest, SearchResponse
from app.services.search import run_search

app = FastAPI(title="EstateFlow Search Service", version="0.1.0")


@app.get("/health")
async def health():
    return {"ok": True, "service": "estateflow-search"}


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    try:
        items = await run_search(request)
        return SearchResponse(status="ok", totalFound=len(items), items=items)
    except Exception as error:
        return SearchResponse(status="error", error=str(error), totalFound=0, items=[])
