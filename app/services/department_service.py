import logging
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.department import Department
from app.models.employee import Employee
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentDetailResponse
from app.schemas.employee import EmployeeCreate, EmployeeResponse
from app.utils.validators import check_cycle, get_descendants_ids

logger = logging.getLogger(__name__)

class DepartmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_department(self, department_data: DepartmentCreate) -> Department:
        if department_data.parent_id:
            parent = await self.db.get(Department, department_data.parent_id)
            if not parent:
                raise ValueError(f"Parent department {department_data.parent_id} not found")
            
            if await check_cycle(self.db, department_data.parent_id, None):
                raise ValueError("Cannot create department that would create a cycle")
        
        existing = await self.db.execute(
            select(Department).where(
                Department.parent_id == department_data.parent_id,
                func.lower(Department.name) == department_data.name.lower()
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Department with name '{department_data.name}' already exists under this parent")
        
        department = Department(
            name=department_data.name.strip(),
            parent_id=department_data.parent_id
        )
        self.db.add(department)
        await self.db.commit()
        await self.db.refresh(department)
        return department

    async def create_employee(self, department_id: int, employee_data: EmployeeCreate) -> Employee:
        department = await self.db.get(Department, department_id)
        if not department:
            raise ValueError(f"Department {department_id} not found")
        
        employee = Employee(
            department_id=department_id,
            full_name=employee_data.full_name.strip(),
            position=employee_data.position.strip(),
            hired_at=employee_data.hired_at
        )
        self.db.add(employee)
        await self.db.commit()
        await self.db.refresh(employee)
        return employee

    async def get_department(self, department_id: int, depth: int, include_employees: bool) -> Optional[DepartmentDetailResponse]:
        query = select(Department).where(Department.id == department_id)
        if include_employees:
            query = query.options(selectinload(Department.employees))
        
        result = await self.db.execute(query)
        department = result.scalar_one_or_none()
        
        if not department:
            return None
        
        return await self._build_department_tree(department, depth, include_employees)

    async def _build_department_tree(self, department: Department, depth: int, include_employees: bool) -> DepartmentDetailResponse:
        employees = []
        if include_employees and department.employees:
            employees = [
                EmployeeResponse.model_validate(emp)
                for emp in sorted(department.employees, key=lambda e: e.created_at or e.full_name)
            ]
        
        children = []
        if depth > 1:
            child_query = select(Department).where(Department.parent_id == department.id)
            if include_employees:
                child_query = child_query.options(selectinload(Department.employees))
            
            result = await self.db.execute(child_query)
            children_deps = result.scalars().all()
            
            for child in children_deps:
                child_tree = await self._build_department_tree(child, depth - 1, include_employees)
                children.append(child_tree)
        
        return DepartmentDetailResponse(
            id=department.id,
            name=department.name,
            parent_id=department.parent_id,
            created_at=department.created_at,
            employees=employees,
            children=children
        )

    async def update_department(self, department_id: int, update_data: DepartmentUpdate) -> Optional[Department]:
        department = await self.db.get(Department, department_id)
        if not department:
            return None
        
        if update_data.name:
            name_stripped = update_data.name.strip()
            existing = await self.db.execute(
                select(Department).where(
                    Department.parent_id == department.parent_id,
                    func.lower(Department.name) == name_stripped.lower(),
                    Department.id != department_id
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Department with name '{name_stripped}' already exists under this parent")
            department.name = name_stripped
        
        if update_data.parent_id is not None:
            if update_data.parent_id == department_id:
                raise ValueError("Department cannot be parent of itself")
            
            if update_data.parent_id:
                new_parent = await self.db.get(Department, update_data.parent_id)
                if not new_parent:
                    raise ValueError(f"Parent department {update_data.parent_id} not found")
                
                if await check_cycle(self.db, update_data.parent_id, department_id):
                    raise ValueError("Cannot move department: this would create a cycle")
            
            department.parent_id = update_data.parent_id
        
        await self.db.commit()
        await self.db.refresh(department)
        return department

    async def delete_department(self, department_id: int, mode: str, reassign_to_id: Optional[int]) -> bool:
        department = await self.db.get(Department, department_id)
        if not department:
            return False
        
        if mode == "cascade":
            await self.db.delete(department)
            await self.db.commit()
            return True
        
        elif mode == "reassign":
            target_department = await self.db.get(Department, reassign_to_id)
            if not target_department:
                raise ValueError(f"Target department {reassign_to_id} not found")
            
            descendants_ids = await get_descendants_ids(self.db, department_id)
            all_to_delete = [department_id] + descendants_ids
            
            for dept_id in all_to_delete:
                await self.db.execute(
                    Employee.__table__.update()
                    .where(Employee.department_id == dept_id)
                    .values(department_id=reassign_to_id)
                )
            
            for dept_id in all_to_delete:
                dept = await self.db.get(Department, dept_id)
                if dept:
                    await self.db.delete(dept)
            
            await self.db.commit()
            return True
        
        return False
