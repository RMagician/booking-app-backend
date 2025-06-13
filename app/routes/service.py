"""
Service API routes module
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status

from app.repositories.service_repository import ServiceRepository
from app.schemas.service import (
    ServiceCreate,
    ServiceUpdate,
    ServiceRead,
    PaginatedServiceRead,  # Added PaginatedServiceRead
)

# Define the router with the "services" tag
router = APIRouter(tags=["services"])


@router.get(
    "/services", response_model=PaginatedServiceRead
)  # Changed ServiceList to PaginatedServiceRead
async def list_services(
    skip: int = Query(0, ge=0, description="Number of services to skip"),
    limit: int = Query(
        100, ge=1, le=500, description="Maximum number of services to return"
    ),
    sort_by: str = Query("name", description="Field to sort by"),
    sort_direction: int = Query(
        1, ge=-1, le=1, description="Sort direction (1=asc, -1=desc)"
    ),
    category: Optional[str] = Query(
        None, description="Filter by category"
    ),  # Added category query parameter
    service_repo: ServiceRepository = Depends(lambda: ServiceRepository()),
) -> PaginatedServiceRead:  # Changed ServiceList to PaginatedServiceRead
    """
    List all services with pagination and sorting options
    """
    services, count = await service_repo.list_services(
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_direction=sort_direction,
        category=category,  # Pass category to repository
    )

    return PaginatedServiceRead(  # Changed ServiceList to PaginatedServiceRead
        services=[ServiceRead.model_validate(service) for service in services],
        count=count,
        page=skip // limit + 1 if limit > 0 else 1,  # Calculate page
        size=limit,  # Use limit as size
    )


@router.post(
    "/services", response_model=ServiceRead, status_code=status.HTTP_201_CREATED
)
async def create_service(
    service_data: ServiceCreate,
    service_repo: ServiceRepository = Depends(lambda: ServiceRepository()),
) -> ServiceRead:
    """
    Create a new service
    """
    service = await service_repo.create_service(service_data.model_dump())
    return ServiceRead.model_validate(service)


@router.get("/services/{service_id}", response_model=ServiceRead)
async def get_service(
    service_id: str = Path(
        ..., description="The ID of the service to retrieve"
    ),
    service_repo: ServiceRepository = Depends(lambda: ServiceRepository()),
) -> ServiceRead:
    """
    Get a service by ID
    """
    service = await service_repo.get_service(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with ID {service_id} not found",
        )
    return ServiceRead.model_validate(service)


@router.put("/services/{service_id}", response_model=ServiceRead)
async def update_service(
    service_data: ServiceUpdate,
    service_id: str = Path(..., description="The ID of the service to update"),
    service_repo: ServiceRepository = Depends(lambda: ServiceRepository()),
) -> ServiceRead:
    """
    Update a service by ID
    """
    # Filter out None values to prevent overwriting with None
    update_data = {
        k: v for k, v in service_data.model_dump().items() if v is not None
    }

    updated_service = await service_repo.update_service(service_id, update_data)
    if not updated_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with ID {service_id} not found",
        )
    return ServiceRead.model_validate(updated_service)


@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: str = Path(..., description="The ID of the service to delete"),
    service_repo: ServiceRepository = Depends(lambda: ServiceRepository()),
) -> None:
    """
    Delete a service by ID
    """
    deleted = await service_repo.delete_service(service_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with ID {service_id} not found",
        )
    return None
