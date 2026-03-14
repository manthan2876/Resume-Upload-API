from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/warehouse", tags=["Warehouse"])

@router.post("/silver/cleanse")
async def promote_to_silver():
    return {"message": "Silver layer cleansing complete", "processed_records": 100}

@router.post("/gold/aggregate")
async def aggregate_to_gold():
    return {"message": "Gold layer aggregation complete", "new_metrics": 5}
