import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.firebase import db
from app.domain.models import RESTAURANTS_COLLECTION
from app.main import app

client = TestClient(app)
API = "/api/v1/restaurants"


def payload(**overrides):
    data = {
        "name": "Restaurante Test",
        "category": "Mexicana",
        "city": "Puebla",
        "price": 2,
    }
    data.update(overrides)
    return data


@pytest.fixture
def created_ids():
    """Registra los documentos creados en cada prueba y los borra al terminar."""
    ids = []
    yield ids
    for restaurant_id in ids:
        db.collection(RESTAURANTS_COLLECTION).document(restaurant_id).delete()


@pytest.fixture
def make_restaurant(created_ids):
    def _make(**overrides):
        response = client.post(API, json=payload(**overrides))
        assert response.status_code == 201, response.text
        body = response.json()
        created_ids.append(body["id"])
        return body

    return _make


@pytest.fixture
def unique_city():
    """Ciudad única para aislar cada prueba de los datos semilla."""
    return f"Ciudad-{uuid.uuid4().hex[:8]}"


# ---------- Salud ----------

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------- Crear (HU-01) ----------

def test_create_restaurant(make_restaurant):
    body = make_restaurant()
    assert body["name"] == "Restaurante Test"
    assert body["id"]
    assert body["avgRating"] == 0
    assert body["numRatings"] == 0


def test_create_is_persisted(make_restaurant):
    body = make_restaurant(name="Persistido")
    response = client.get(f"{API}/{body['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Persistido"


def test_create_strips_whitespace_and_empty_photo_is_none(make_restaurant):
    body = make_restaurant(name="  Con espacios  ", photoUrl="   ")
    assert body["name"] == "Con espacios"
    assert body["photoUrl"] is None


@pytest.mark.parametrize("price", [0, 4, 10, -1])
def test_invalid_price(price):
    response = client.post(API, json=payload(price=price))
    assert response.status_code == 422


def test_invalid_price_type():
    response = client.post(API, json=payload(price="caro"))
    assert response.status_code == 422


@pytest.mark.parametrize("field", ["name", "category", "city", "price"])
def test_missing_required_field(field):
    data = payload()
    data.pop(field)
    assert client.post(API, json=data).status_code == 422


@pytest.mark.parametrize("field", ["name", "category", "city"])
def test_blank_text_field(field):
    assert client.post(API, json=payload(**{field: "   "})).status_code == 422


def test_name_too_long():
    assert client.post(API, json=payload(name="x" * 101)).status_code == 422


@pytest.mark.parametrize("url", ["javascript:alert(1)", "ftp://x.com/a.png", "no-es-url"])
def test_invalid_photo_url(url):
    assert client.post(API, json=payload(photoUrl=url)).status_code == 422


# ---------- Ver detalle (HU-03) ----------

def test_get_restaurant(make_restaurant):
    created = make_restaurant()
    response = client.get(f"{API}/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_restaurant_not_found():
    response = client.get(f"{API}/no-existe-123")
    assert response.status_code == 404
    assert response.json()["detail"] == "Restaurante no encontrado"


# ---------- Listar y filtrar (HU-02) ----------

def test_list_returns_list():
    response = client.get(API)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_respects_limit(make_restaurant, unique_city):
    for i in range(3):
        make_restaurant(name=f"R{i}", city=unique_city)
    response = client.get(API, params={"city": unique_city, "limit": 2})
    assert len(response.json()) == 2


def test_list_invalid_limit():
    assert client.get(API, params={"limit": 0}).status_code == 422
    assert client.get(API, params={"limit": 101}).status_code == 422


def test_filter_by_city(make_restaurant, unique_city):
    make_restaurant(name="En ciudad", city=unique_city)
    make_restaurant(name="Otra ciudad", city="Otra-" + unique_city)
    names = [r["name"] for r in client.get(API, params={"city": unique_city}).json()]
    assert names == ["En ciudad"]


def test_filter_by_category(make_restaurant, unique_city):
    make_restaurant(name="Pizzas", category="Pizza", city=unique_city)
    make_restaurant(name="Tacos", category="Tacos", city=unique_city)
    result = client.get(API, params={"city": unique_city, "category": "Pizza"}).json()
    assert [r["name"] for r in result] == ["Pizzas"]


def test_filter_by_price(make_restaurant, unique_city):
    make_restaurant(name="Barato", price=1, city=unique_city)
    make_restaurant(name="Caro", price=3, city=unique_city)
    result = client.get(API, params={"city": unique_city, "price": 3}).json()
    assert [r["name"] for r in result] == ["Caro"]


def test_filter_combined(make_restaurant, unique_city):
    make_restaurant(name="A", category="Pizza", price=1, city=unique_city)
    make_restaurant(name="B", category="Pizza", price=3, city=unique_city)
    make_restaurant(name="C", category="Tacos", price=3, city=unique_city)
    result = client.get(
        API, params={"city": unique_city, "category": "Pizza", "price": 3}
    ).json()
    assert [r["name"] for r in result] == ["B"]


def test_filter_invalid_price():
    assert client.get(API, params={"price": 9}).status_code == 422


def test_order_by_name(make_restaurant, unique_city):
    for name in ["Cantina", "Antojitos", "Bistro"]:
        make_restaurant(name=name, city=unique_city)
    result = client.get(API, params={"city": unique_city, "order_by": "name"}).json()
    assert [r["name"] for r in result] == ["Antojitos", "Bistro", "Cantina"]


def test_order_by_rating_desc(make_restaurant, unique_city):
    ratings = {"Regular": 3.0, "Excelente": 4.9, "Bueno": 4.0}
    for name, rating in ratings.items():
        created = make_restaurant(name=name, city=unique_city)
        db.collection(RESTAURANTS_COLLECTION).document(created["id"]).update(
            {"avgRating": rating, "numRatings": 5}
        )
    result = client.get(API, params={"city": unique_city, "order_by": "avgRating"}).json()
    assert [r["name"] for r in result] == ["Excelente", "Bueno", "Regular"]


def test_invalid_order_by():
    assert client.get(API, params={"order_by": "price"}).status_code == 422


def test_pagination_with_start_after(make_restaurant, unique_city):
    for name in ["A", "B", "C"]:
        make_restaurant(name=name, city=unique_city)
    params = {"city": unique_city, "limit": 2}
    first = client.get(API, params=params).json()
    assert [r["name"] for r in first] == ["A", "B"]
    second = client.get(API, params={**params, "start_after": first[-1]["id"]}).json()
    assert [r["name"] for r in second] == ["C"]


# ---------- Editar (HU-04) ----------

def test_update_only_sent_fields(make_restaurant):
    created = make_restaurant(name="Original", category="Pizza", price=1)
    response = client.patch(f"{API}/{created['id']}", json={"name": "Nuevo nombre"})
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Nuevo nombre"
    assert body["category"] == "Pizza"
    assert body["price"] == 1


def test_update_ignores_non_editable_fields(make_restaurant):
    created = make_restaurant()
    response = client.patch(
        f"{API}/{created['id']}",
        json={"name": "Editado", "avgRating": 5, "numRatings": 999, "id": "otro"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["avgRating"] == 0
    assert body["numRatings"] == 0
    assert body["id"] == created["id"]


def test_update_can_clear_photo(make_restaurant):
    created = make_restaurant(photoUrl="https://example.com/a.jpg")
    response = client.patch(f"{API}/{created['id']}", json={"photoUrl": ""})
    assert response.status_code == 200
    assert response.json()["photoUrl"] is None


def test_update_without_fields_returns_400(make_restaurant):
    created = make_restaurant()
    assert client.patch(f"{API}/{created['id']}", json={}).status_code == 400


def test_update_invalid_price(make_restaurant):
    created = make_restaurant()
    assert client.patch(f"{API}/{created['id']}", json={"price": 7}).status_code == 422


def test_update_not_found():
    response = client.patch(f"{API}/no-existe-123", json={"name": "X"})
    assert response.status_code == 404


# ---------- Eliminar (HU-05) ----------

def test_delete_restaurant(make_restaurant):
    created = make_restaurant()
    response = client.delete(f"{API}/{created['id']}")
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"{API}/{created['id']}").status_code == 404


def test_delete_not_found():
    assert client.delete(f"{API}/no-existe-123").status_code == 404


# ---------- Vistas HTML ----------

def test_home_lists_restaurants(make_restaurant, unique_city):
    make_restaurant(name="Visible en home", city=unique_city)
    response = client.get("/", params={"city": unique_city})
    assert response.status_code == 200
    assert "Visible en home" in response.text
    assert "Ver detalles" in response.text


def test_home_filters_in_html(make_restaurant, unique_city):
    make_restaurant(name="Barato HTML", price=1, city=unique_city)
    make_restaurant(name="Caro HTML", price=3, city=unique_city)
    response = client.get("/", params={"city": unique_city, "price": "3"})
    assert "Caro HTML" in response.text
    assert "Barato HTML" not in response.text


def test_home_accepts_empty_filters():
    # El formulario HTML envía los filtros vacíos (price="").
    response = client.get("/", params={"city": "", "category": "", "price": ""})
    assert response.status_code == 200


def test_home_empty_state(unique_city):
    response = client.get("/", params={"city": unique_city})
    assert response.status_code == 200
    assert "No hay restaurantes" in response.text


def test_new_form_view():
    response = client.get("/restaurants/new")
    assert response.status_code == 200
    assert 'id="restaurant-form"' in response.text
    assert 'data-mode="create"' in response.text


def test_detail_view(make_restaurant):
    created = make_restaurant(name="Detalle HTML")
    response = client.get(f"/restaurants/{created['id']}")
    assert response.status_code == 200
    assert "Detalle HTML" in response.text
    assert "Editar" in response.text
    assert "Eliminar" in response.text


def test_detail_view_not_found():
    response = client.get("/restaurants/no-existe-123")
    assert response.status_code == 404
    assert "text/html" in response.headers["content-type"]


def test_edit_form_is_prefilled(make_restaurant):
    created = make_restaurant(name="Para editar", price=3)
    response = client.get(f"/restaurants/{created['id']}/edit")
    assert response.status_code == 200
    assert 'data-mode="edit"' in response.text
    assert "Para editar" in response.text
    assert 'value="3" selected' in response.text


def test_edit_form_not_found():
    assert client.get("/restaurants/no-existe-123/edit").status_code == 404
