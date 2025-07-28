from routers.api_gateway import ServiceRoute

routes = [
    ServiceRoute(
        path="/products",
        target_url="http://product-service:8000/products",
        methods=["GET", "POST"],
        required_scopes=["products:read", "products:write"]
    ),
    ServiceRoute(
        path="/orders",
        target_url="http://order-service:8000/orders",
        methods=["GET", "POST"],
        required_scopes=["orders:read", "orders:write"]
    ),
    ServiceRoute(
        path="/users",
        target_url="http://user-service:8000/users",
        methods=["GET"],
        required_scopes=["admin"]
    ),
]