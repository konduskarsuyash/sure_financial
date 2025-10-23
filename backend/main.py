from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from parser_router import route_parser


app = FastAPI(title="CC Statement Parser", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://sure-financial.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/parse")
async def parse_statement(file: UploadFile = File(...), issuer: str | None = Form(None)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    pdf_bytes = await file.read()

    result = route_parser(pdf_bytes, issuer_hint=issuer)

    return JSONResponse(content=result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)