from fastapi import APIRouter, Request, HTTPException, Depends
from auth import get_current_active_user, has_required_scopes
import httpx
from service_routes import routes
from pydantic import BaseModel
from typing import List

router = APIRouter()

class ServiceRoute(BaseModel):
    path: str
    target_url: str
    methods: List[str]
    required_scopes: List[str] = []

@router.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway_proxy(
    path_name: str,
    request: Request,
    current_user: dict = Depends(get_current_active_user)
):
    matched_route = None
    for route in routes:
        if path_name.startswith(route.path):
            matched_route = route
            break
    
    if not matched_route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    if request.method not in matched_route.methods:
        raise HTTPException(status_code=405, detail="Method not allowed")
    
    if not has_required_scopes(matched_route.required_scopes, current_user.scopes):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    target_url = matched_route.target_url + path_name[len(matched_route.path):]
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                request.method,
                target_url,
                headers=dict(request.headers),
                params=dict(request.query_params),
                data=await request.body()
            )
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=str(e))