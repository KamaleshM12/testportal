from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from .schemas import ExecutionRequest, ExecutionResult
from .executor import execute

app = FastAPI(title='Secure Code Runner')


@app.post('/execute', response_model=ExecutionResult)
async def run_code(req: ExecutionRequest):
    try:
        res = execute(req.code, req.language, req.tests)
        return JSONResponse(status_code=200, content=res)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail='execution error')
