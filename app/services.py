# Microservice routing
# services.py
import httpx
from fastapi import HTTPException

SERVICE_URLS = {
    "user_service": "http://user-service:8001",
    "product_service": "http://product-service:8002",
    "order_service": "http://order-service:8003"
}

async def route_request(service_name: str, path: str, method: str, headers: dict, body: bytes):
    if service_name not in SERVICE_URLS:
        raise HTTPException(status_code=404, detail="Service not found")
    
    url = f"{SERVICE_URLS[service_name]}/{path}"
    
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, headers=headers, content=body)
            elif method == "PUT":
                response = await client.put(url, headers=headers, content=body)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))