from typing import Literal

from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.restaurants import router as restaurants_router
from app.services.restaurant_service import RestaurantService

app = FastAPI(title="FriendlyEats FastAPI")
app.include_router(restaurants_router, prefix="/api/v1")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")
service = RestaurantService()

PAGE_SIZE = 20


@app.exception_handler(StarletteHTTPException)
async def html_or_json_errors(request: Request, exc: StarletteHTTPException):
    """La API responde JSON; las vistas HTML responden una página de error."""
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exc)
    return templates.TemplateResponse(
        request,
        "error.html",
        {"status_code": exc.status_code, "detail": exc.detail},
        status_code=exc.status_code,
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


# ---------- Vistas HTML ----------

@app.get("/")
async def home(
    request: Request,
    city: str = "",
    category: str = "",
    price: str = "",
    order_by: Literal["name", "avgRating"] = "name",
    start_after: str = "",
    msg: str = "",
):
    price_value = int(price) if price in ("1", "2", "3") else None
    restaurants = service.list(
        category=category.strip() or None,
        city=city.strip() or None,
        price=price_value,
        order_by=order_by,
        limit=PAGE_SIZE,
        start_after=start_after or None,
    )
    next_cursor = restaurants[-1]["id"] if len(restaurants) == PAGE_SIZE else None
    return templates.TemplateResponse(
        request,
        "restaurants.html",
        {
            "restaurants": restaurants,
            "filters": {
                "city": city,
                "category": category,
                "price": price,
                "order_by": order_by,
            },
            "facets": service.facets(),
            "next_cursor": next_cursor,
            "msg": msg,
        },
    )


# "new" debe declararse antes que "{restaurant_id}".
@app.get("/restaurants/new")
async def new_restaurant_form(request: Request):
    return templates.TemplateResponse(request, "restaurant_form.html", {"restaurant": None})


@app.get("/restaurants/{restaurant_id}")
async def restaurant_detail(request: Request, restaurant_id: str, msg: str = ""):
    restaurant = service.get(restaurant_id)  # 404 si no existe
    return templates.TemplateResponse(
        request, "restaurant_detail.html", {"restaurant": restaurant, "msg": msg}
    )


@app.get("/restaurants/{restaurant_id}/edit")
async def edit_restaurant_form(request: Request, restaurant_id: str):
    restaurant = service.get(restaurant_id)
    return templates.TemplateResponse(request, "restaurant_form.html", {"restaurant": restaurant})
