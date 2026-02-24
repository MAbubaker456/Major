from fastapi import APIRouter
from backend.app.services.code_assist.ingestion_service import ingest_repository
from backend.app.services.code_assist.query_service import ask_question

router = APIRouter(prefix="/code-assist", tags=["Code Assist"])


@router.post("/index/{repo_id}")
def index_repo(repo_id: str):
    return ingest_repository(repo_id)


@router.post("/ask/{repo_id}")
def ask(repo_id: str, payload: dict):
    question = payload.get("question")
    return ask_question(repo_id, question)