"""Constantes del dominio de restaurantes."""

RESTAURANTS_COLLECTION = "restaurants"

# Campos por los que se permite ordenar el listado.
ORDER_FIELDS = ("name", "avgRating")

# Campos que un administrador puede editar (PATCH).
EDITABLE_FIELDS = ("name", "category", "city", "price", "photoUrl")

PRICE_LABELS = {1: "$", 2: "$$", 3: "$$$"}
