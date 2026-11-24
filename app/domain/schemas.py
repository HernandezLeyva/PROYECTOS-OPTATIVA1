from pydantic import BaseModel, ConfigDict, Field, field_validator


def _clean_photo_url(value: str | None) -> str | None:
    """Vacío -> None. Solo se aceptan URLs http(s)."""
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    if not value.lower().startswith(("http://", "https://")):
        raise ValueError("photoUrl debe iniciar con http:// o https://")
    if len(value) > 500:
        raise ValueError("photoUrl es demasiado larga (máximo 500 caracteres)")
    return value


class RestaurantBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    city: str = Field(min_length=1, max_length=50)
    price: int = Field(ge=1, le=3)
    photoUrl: str | None = None

    _check_photo = field_validator("photoUrl")(_clean_photo_url)


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantUpdate(BaseModel):
    """Solo campos editables; cualquier otro campo enviado se ignora."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=100)
    category: str | None = Field(default=None, min_length=1, max_length=50)
    city: str | None = Field(default=None, min_length=1, max_length=50)
    price: int | None = Field(default=None, ge=1, le=3)
    photoUrl: str | None = None

    _check_photo = field_validator("photoUrl")(_clean_photo_url)


class RestaurantResponse(RestaurantBase):
    id: str
    avgRating: float = 0
    numRatings: int = 0
