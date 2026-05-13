import pytest
import httpx

@pytest.mark.asyncio
async def test_create_employee():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # First create a department
        dept_response = await client.post("/departments/", json={"name": "HR Dept", "parent_id": None})
        dept_id = dept_response.json()["id"]
        
        # Create employee
        response = await client.post(f"/departments/{dept_id}/employees/", json={"full_name": "John Doe", "position": "Developer"})
        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == "John Doe"

@pytest.mark.asyncio
async def test_create_employee_with_hired_date():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Create department
        dept_response = await client.post("/departments/", json={"name": "IT Dept", "parent_id": None})
        dept_id = dept_response.json()["id"]
        
        # Create employee with hired date
        response = await client.post(f"/departments/{dept_id}/employees/", json={
            "full_name": "Jane Smith", 
            "position": "Manager",
            "hired_at": "2024-01-15"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == "Jane Smith"
        assert data["hired_at"] == "2024-01-15"