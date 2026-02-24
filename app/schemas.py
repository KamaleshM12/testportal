from pydantic import BaseModel
from typing import List, Optional


class TestCase(BaseModel):
    input: str
    expected_output: str


class ExecutionRequest(BaseModel):
    code: str
    language: str
    tests: List[TestCase]


class TestResult(BaseModel):
    stdout: str
    stderr: Optional[str] = None
    time_seconds: Optional[float] = None
    memory_kb: Optional[int] = None
    passed: bool


class ExecutionResult(BaseModel):
    compile_success: bool
    compile_output: Optional[str] = None
    tests: List[TestResult]
