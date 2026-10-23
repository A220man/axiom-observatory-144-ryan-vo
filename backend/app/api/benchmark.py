from fastapi import APIRouter, HTTPException, status
from app.models.schemas import BenchmarkRequest, BenchmarkResponse, HealthResponse
from app.services.inference import inference_service

router = APIRouter(prefix="/api/v1", tags=["benchmark"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse()


@router.post("/benchmark", response_model=BenchmarkResponse, status_code=status.HTTP_200_OK)
async def run_benchmark(request: BenchmarkRequest):
    """Run inference benchmark."""
    try:
        result = await inference_service.run_benchmark(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Benchmark failed: {str(e)}"
        )