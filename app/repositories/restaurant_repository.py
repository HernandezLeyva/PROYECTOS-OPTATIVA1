from google.cloud.firestore_v1 import Query
from google.cloud.firestore_v1.base_query import FieldFilter

from app.core.firebase import db
from app.domain.models import RESTAURANTS_COLLECTION


class RestaurantRepository:
    """Aísla todo el acceso a Firestore."""

    def __init__(self):
        self.collection = db.collection(RESTAURANTS_COLLECTION)

    def create(self, data: dict) -> dict:
        ref = self.collection.document()  # ID automático
        data["id"] = ref.id
        data["avgRating"] = 0
        data["numRatings"] = 0
        ref.set(data)
        return data

    def get(self, restaurant_id: str):
        doc = self.collection.document(restaurant_id).get()
        if not doc.exists:
            return None
        return doc.to_dict() | {"id": doc.id}

    def list(
        self,
        category: str | None = None,
        city: str | None = None,
        price: int | None = None,
        order_by: str = "name",
        limit: int = 20,
        start_after: str | None = None,
    ):
        query = self.collection
        has_filters = bool(category or city or price)

        if category:
            query = query.where(filter=FieldFilter("category", "==", category))
        if city:
            query = query.where(filter=FieldFilter("city", "==", city))
        if price:
            query = query.where(filter=FieldFilter("price", "==", price))

        # Firestore requiere índices compuestos para combinar where() + order_by()
        # en campos distintos. Para evitar ese error, cuando hay filtros activos
        # traemos más documentos y ordenamos en memoria.
        if has_filters:
            fetch_limit = 500
            results = [doc.to_dict() | {"id": doc.id} for doc in query.limit(fetch_limit).stream()]
            reverse = order_by == "avgRating"
            results.sort(key=lambda r: r.get(order_by, 0 if reverse else ""), reverse=reverse)
            # Paginación manual por cursor cuando hay filtros
            if start_after:
                ids = [r["id"] for r in results]
                if start_after in ids:
                    idx = ids.index(start_after) + 1
                    results = results[idx:]
            return results[:limit]

        # Sin filtros: Firestore ordena de forma nativa (más eficiente)
        direction = Query.DESCENDING if order_by == "avgRating" else Query.ASCENDING
        query = query.order_by(order_by, direction=direction).limit(limit)

        if start_after:
            last_doc = self.collection.document(start_after).get()
            if last_doc.exists:
                query = query.start_after(last_doc)

        return [doc.to_dict() | {"id": doc.id} for doc in query.stream()]

    def facets(self) -> dict:
        """Ciudades y categorías existentes (para sugerir en los filtros)."""
        cities, categories = set(), set()
        for doc in self.collection.select(["city", "category"]).limit(500).stream():
            data = doc.to_dict()
            if data.get("city"):
                cities.add(data["city"])
            if data.get("category"):
                categories.add(data["category"])
        return {"cities": sorted(cities), "categories": sorted(categories)}

    def update(self, restaurant_id: str, data: dict) -> dict | None:
        ref = self.collection.document(restaurant_id)
        doc = ref.get()

        if not doc.exists:
            return None

        ref.update(data)
        return self.get(restaurant_id)

    def delete(self, restaurant_id: str) -> bool:
        ref = self.collection.document(restaurant_id)
        doc = ref.get()

        if not doc.exists:
            return False

        ref.delete()
        return True
