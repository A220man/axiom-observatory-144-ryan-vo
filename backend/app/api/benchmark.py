from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import BenchmarkRequest, BenchmarkResponse, HealthResponse
from app.services.inference import inference_service
from app.api.auth import require_auth

router = APIRouter(prefix="/api/v1", tags=["benchmark"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse()


@router.post("/benchmark", response_model=BenchmarkResponse, status_code=status.HTTP_200_OK)
async def run_benchmark(request: BenchmarkRequest, user=Depends(require_auth)):
    """Run inference benchmark."""
    try:
        result = await inference_service.run_benchmark(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Benchmark failed: {str(e)}"
        )