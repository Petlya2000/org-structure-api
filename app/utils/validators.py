from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.department import Department
from typing import List

async def check_cycle(db: AsyncSession, new_parent_id: int, department_id: int) -> bool:
    if not new_parent_id:
        return False
    
    current_id = new_parent_id
    visited = set()
    
    while current_id and current_id not in visited:
        if current_id == department_id:
            return True
        visited.add(current_id)
        
        dept = await db.get(Department, current_id)
        if not dept:
            break
        current_id = dept.parent_id
    
    return False

async def get_descendants_ids(db: AsyncSession, department_id: int) -> List[int]:
    descendants = []
    
    async def collect_children(parent_id: int):
        result = await db.execute(
            select(Department.id).where(Department.parent_id == parent_id)
        )
        children_ids = result.scalars().all()
        
        for child_id in children_ids:
            descendants.append(child_id)
            await collect_children(child_id)
    
    await collect_children(department_id)
    return descendants
