"""Datos semilla: 10 restaurantes de prueba.

Usa IDs fijos con set(), por lo que se puede ejecutar varias veces
sin duplicar documentos:  python -m scripts.seed
"""
from app.core.firebase import db
from app.domain.models import RESTAURANTS_COLLECTION

restaurants = [
    {
        "id": "la-abuela",
        "name": "La Abuela",
        "category": "Mexicana",
        "city": "Puebla",
        "price": 2,
        "photoUrl": "https://images.unsplash.com/photo-1552566626-52f8b828add9",
        "avgRating": 4.5,
        "numRatings": 20,
    },
    {
        "id": "pizza-central",
        "name": "Pizza Central",
        "category": "Pizza",
        "city": "Puebla",
        "price": 1,
        "photoUrl": "https://images.unsplash.com/photo-1513104890138-7c749659a591",
        "avgRating": 4.0,
        "numRatings": 12,
    },
    {
        "id": "mole-don-ramon",
        "name": "Mole Don Ramón",
        "category": "Mexicana",
        "city": "Puebla",
        "price": 2,
        "photoUrl": None,
        "avgRating": 4.7,
        "numRatings": 35,
    },
    {
        "id": "cemitas-la-poblanita",
        "name": "Cemitas La Poblanita",
        "category": "Antojitos",
        "city": "Puebla",
        "price": 1,
        "photoUrl": None,
        "avgRating": 4.3,
        "numRatings": 28,
    },
    {
        "id": "tacos-arabes-el-zocalo",
        "name": "Tacos Árabes El Zócalo",
        "category": "Tacos",
        "city": "Puebla",
        "price": 1,
        "photoUrl": None,
        "avgRating": 4.6,
        "numRatings": 41,
    },
    {
        "id": "casa-del-chile-en-nogada",
        "name": "Casa del Chile en Nogada",
        "category": "Mexicana",
        "city": "Puebla",
        "price": 3,
        "photoUrl": None,
        "avgRating": 4.8,
        "numRatings": 17,
    },
    {
        "id": "sushi-angelopolis",
        "name": "Sushi Angelópolis",
        "category": "Japonesa",
        "city": "Puebla",
        "price": 3,
        "photoUrl": None,
        "avgRating": 4.2,
        "numRatings": 15,
    },
    {
        "id": "cafe-los-sapos",
        "name": "Café Los Sapos",
        "category": "Cafetería",
        "city": "Puebla",
        "price": 1,
        "photoUrl": None,
        "avgRating": 4.1,
        "numRatings": 9,
    },
    {
        "id": "trattoria-cholula",
        "name": "Trattoria Cholula",
        "category": "Italiana",
        "city": "Cholula",
        "price": 3,
        "photoUrl": None,
        "avgRating": 4.4,
        "numRatings": 22,
    },
    {
        "id": "mariscos-la-bahia",
        "name": "Mariscos La Bahía",
        "category": "Mariscos",
        "city": "Atlixco",
        "price": 2,
        "photoUrl": None,
        "avgRating": 3.9,
        "numRatings": 11,
    },
]

for restaurant in restaurants:
    doc_id = restaurant["id"]
    db.collection(RESTAURANTS_COLLECTION).document(doc_id).set(restaurant)

print(f"Datos semilla creados: {len(restaurants)} restaurantes")
