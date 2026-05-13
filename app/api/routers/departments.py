import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db
from app.services.department_service import DepartmentService
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse, DepartmentDetailResponse
from app.schemas.employee import EmployeeCreate, EmployeeResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=DepartmentResponse, status_code=201)
async def create_department(
    department: DepartmentCreate,
    db: AsyncSession = Depends(get_db)
):
    service = DepartmentService(db)
    try:
        result = await service.create_department(department)
        logger.info(f"Created department: {result.id} - {result.name}")
        return result
    except ValueError as e:
        logger.warning(f"Failed to create department: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{department_id}/employees/", response_model=EmployeeResponse, status_code=201)
async def create_employee(
    department_id: int = Path(..., description="Department ID"),
    employee: EmployeeCreate = None,
    db: AsyncSession = Depends(get_db)
):
    service = DepartmentService(db)
    try:
        result = await service.create_employee(department_id, employee)
        logger.info(f"Created employee: {result.id} in department {department_id}")
        return result
    except ValueError as e:
        logger.warning(f"Failed to create employee: {e}")
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{department_id}", response_model=DepartmentDetailResponse)
async def get_department(
    department_id: int = Path(..., description="Department ID"),
    depth: int = Query(1, ge=1, le=5, description="Depth of nested departments"),
    include_employees: bool = Query(True, description="Include employees in response"),
    db: AsyncSession = Depends(get_db)
):
    service = DepartmentService(db)
    result = await service.get_department(department_id, depth, include_employees)
    if not result:
        raise HTTPException(status_code=404, detail="Department not found")
    return result

@router.patch("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    department_update: DepartmentUpdate,
    db: AsyncSession = Depends(get_db)
):
    service = DepartmentService(db)
    try:
        result = await service.update_department(department_id, department_update)
        if not result:
            raise HTTPException(status_code=404, detail="Department not found")
        logger.info(f"Updated department: {department_id}")
        return result
    except ValueError as e:
        logger.warning(f"Failed to update department: {e}")
        raise HTTPException(status_code=409 if "cycle" in str(e).lower() else 400, detail=str(e))

@router.delete("/{department_id}", status_code=204)
async def delete_department(
    department_id: int,
    mode: str = Query(..., description="cascade or reassign"),
    reassign_to_department_id: Optional[int] = Query(None, description="Required if mode=reassign"),
    db: AsyncSession = Depends(get_db)
):
    if mode not in ["cascade", "reassign"]:
        raise HTTPException(status_code=400, detail="Mode must be 'cascade' or 'reassign'")
    
    if mode == "reassign" and reassign_to_department_id is None:
        raise HTTPException(status_code=400, detail="reassign_to_department_id is required for reassign mode")
    
    service = DepartmentService(db)
    try:
        success = await service.delete_department(department_id, mode, reassign_to_department_id)
        if not success:
            raise HTTPException(status_code=404, detail="Department not found")
        logger.info(f"Deleted department: {department_id} with mode {mode}")
        return None
    except ValueError as e:
        logger.warning(f"Failed to delete department: {e}")
        raise HTTPException(status_code=400, detail=str(e))
