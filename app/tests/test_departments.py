import pytest
import httpx

@pytest.mark.asyncio
async def test_create_department():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post("/departments/", json={"name": "Test Dept", "parent_id": None})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Dept"

@pytest.mark.asyncio
async def test_create_duplicate_department():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # First create
        await client.post("/departments/", json={"name": "Duplicate", "parent_id": None})
        # Try to create duplicate
        response = await client.post("/departments/", json={"name": "Duplicate", "parent_id": None})
        assert response.status_code == 400

@pytest.mark.asyncio
async def test_create_employee_invalid_department():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post("/departments/999/employees/", json={"full_name": "Test", "position": "Test"})
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_department_tree():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # First create a department
        dept_response = await client.post("/departments/", json={"name": "Tree Dept", "parent_id": None})
        dept_id = dept_response.json()["id"]
        
        # Create child
        await client.post("/departments/", json={"name": "Child Dept", "parent_id": dept_id})
        
        # Get tree
        response = await client.get(f"/departments/{dept_id}?depth=2&include_employees=true")
        assert response.status_code == 200