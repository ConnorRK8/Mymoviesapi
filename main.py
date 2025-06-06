from fastapi import FastAPI, Body, Path, Query, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from jwt_manager import create_token, validate_token
from fastapi.security import HTTPBearer
from config.database import Session, engine, Base
from models.movie import Movie as MovieModel
from fastapi.encoders import jsonable_encoder

app = FastAPI()#
app.title="Mi primera aplicacion con fast api"#
app.version="0.0.1"

Base.metadata.create_all(bind=engine)

class JWTBearer(HTTPBearer):
    async def _call_(self, request : Request):
        auth = await super()._call_(request) 
        data = validate_token(auth.credentials)
        if data['email'] != "administrador@gmail.com":
            raise HTTPException(status_code=403, detail="Credenciales invalidas")

class User(BaseModel):
    email:str
    password:str

@app.post('/login', tags=['auth'])
def login(user : User):
    if user.email == "administrador@gmail.com" and user.password == "password":
        token: str = create_token(user.dict())
        return JSONResponse(status_code=200, content= token)

class Movie(BaseModel):
    id : int | None = None # Optional para el typing id : Optional[int] = None
    title : str = Field(max_length = 60, min_length=3)#default="Titulo de la pelicula",
    overview : str = Field(max_length = 60, min_length=3)#default="Descripcion de la pelicula",
    year : int = Field(le=2025)#default=2000,
    rating : float = Field(ge=1, le=10)
    category : str = Field(max_length = 60, min_length=3)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Pelicula",
                "overview": "Descripcion de la pelicula",
                "year": 2025,
                "rating": 8.5,
                "category": "Science Fiction"
            }
        }


movies = [
    {
        "id": 1,
        "title": "El Origen",
        "overview": "Un ladrón que roba secretos corporativos a través de la tecnología de compartir sueños recibe la tarea inversa de plantar una idea.",
        "year": 2010,
        "rating": 8.8,
        "category": "Ciencia Ficción"
    },
    {
        "id": 2,
        "title": "Interestelar",
        "overview": "Un equipo de exploradores viaja a través de un agujero de gusano en el espacio en un intento de asegurar la supervivencia de la humanidad.",
        "year": 2014,
        "rating": 8.6,
        "category": "Ciencia Ficción"
    },
    {
        "id": 3,
        "title": "Matrix",
        "overview": "Un hacker informático descubre la verdadera naturaleza de su realidad y su papel en la guerra contra sus controladores.",
        "year": 1999,
        "rating": 8.7,
        "category": "Acción"
    },
    {
        "id": 4,
        "title": "Parásitos",
        "overview": "La codicia y la discriminación de clases amenazan la relación simbiótica entre la adinerada familia Park y la pobre familia Kim.",
        "year": 2019,
        "rating": 8.6,
        "category": "Thriller"
    },
    {
        "id": 5,
        "title": "El Viaje de Chihiro",
        "overview": "Durante la mudanza de su familia, una niña de 10 años entra en un mundo gobernado por dioses, brujas y espíritus.",
        "year": 2001,
        "rating": 8.6,
        "category": "Animación"
    },
    {
        "id": 6,
        "title": "El Caballero de la Noche",
        "overview": "Batman enfrenta al Joker, un criminal que quiere sumir Ciudad Gótica en la anarquía.",
        "year": 2008,
        "rating": 9.0,
        "category": "Acción"
    },
    {
        "id": 7,
        "title": "La vida secreta de tus mascotas",
        "overview": "Max es un perro que vive en un apartamento de Manhattan. Cuando su dueña trae a casa a un mestizo llamado Duke, Max no tarda en sentirse amenazado por su presencia.",
        "year": 2016,
        "rating": 6.5,
        "category": "Animación"
    },
    {
        "id": 8,
        "title": "La vida secreta de tus mascotas 2",
        "overview": "Max y sus amigos deben detener a un grupo de animales que quieren vengarse.",
        "year": 2019,
        "rating": 6.5,
        "category": "Animación"
    },
    {
        "id": 9,
        "title": "El Rey León",
        "overview": "El rey león, de Disney, dirigida por Jon Favreau, viaja a la sabana africana donde ha nacido el futuro rey.",
        "year": 2019,
        "rating": 6.9,
        "category": "Animación"
    },
    {
        "id": 10,
        "title": "Madagascar",
        "overview": "Madagascar es una película de animación de DreamWorks que narra la historia de cuatro animales del zoológico de Nueva York.",
        "year": 2005,
        "rating": 6.9,
        "category": "Animación"
    }
]

@app.get('/', tags=['Home'])
def message():
    return "Hello"

@app.get('/movies', tags=['Movies'], response_model=List[Movie], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies() -> List[Movie]:
    db = Session()
    result = db.query(MovieModel).all()
    return JSONResponse(status_code=200, content= jsonable_encoder(result))

@app.get('/movies/{movie_id}', tags=['Movies'], response_model=Movie, dependencies=[Depends(JWTBearer())])
def get_movie(movie_id: int= Path(ge=1, le=200)) -> Movie:
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.id == movie_id).first()
    if not result:
        return JSONResponse(status_code=404, content= {"message" : "no encontrado"})
    return JSONResponse(status_code=200,content= jsonable_encoder(result))

@app.get('/movies/', tags=['Movies'], response_model=List[Movie], dependencies=[Depends(JWTBearer())])
def get_movie_by_category(category: str  = Query(min_length=5, max_length=25)) -> List[Movie]:
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.category == category).all()
    if not result:
        return JSONResponse(status_code=404, content={"message": "No se encontraron peliculas de esa categoria"})
    return JSONResponse(content= jsonable_encoder(result))

@app.post('/movies', tags=['Movies'], response_model= dict, status_code=201, dependencies=[Depends(JWTBearer())])
def create_movie(movie: Movie) -> dict:
    db = Session()
    #utilizamos el modelo y le pasamos la informacion que vamos a registrar
    new_movie = MovieModel(**movie.model_dump())
    db.add(new_movie)
    db.commit()
    movies.append(movie)
    return JSONResponse(status_code=201 ,content= {"message": "Se ha registrado correctamente"})

    
@app.delete('/movies/{movie_id}', tags=['Movies'], response_model= dict, status_code=200, dependencies=[Depends(JWTBearer())])
def delete_movie(movie_id: int) -> dict:
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.id == movie_id).first()
    if not result:
        return JSONResponse(status_code=404, content={"message": "Pelicula no encontrada"})
    db.delete(result)
    db.commit()
    return JSONResponse(status_code=200,content= {"message": "Se ha eliminado la pelicula correctamente"})

@app.put('/movies/{movie_id}', tags=['Movies'], response_model= dict, status_code=200, dependencies=[Depends(JWTBearer())])
def update_movie(movie_id: int, movie: Movie) -> dict:
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.id == movie_id).first()
    if not result:
        return JSONResponse(status_code=404, content={"message": "Pelicula no encontrada"})
    result.title = movie.title
    result.overview = movie.overview
    result.year = movie.year
    result.rating = movie.rating
    result.category = movie.category
    db.commit()
    return JSONResponse(status_code=200,content= {"message": "Se ha actualizado la pelicula correctamente"})


class computer (BaseModel):
    id : Optional[int] = None
    marca : str = Field(max_length = 25, min_length=2)
    modelo : str = Field(max_length = 25, min_length=2)
    color : str = Field(max_length = 25, min_length=2)
    ram : int = Field(ge=1, le=64)
    almacenamiento : int = Field(ge=1, le=1000)

    class Config:
        json_schema_extra = {
            "example": {
                "marca": "HP",
                "modelo": "Victus 15",
                "color": "Gris",
                "ram": 8,
                "almacenamiento": 512
            }
        }
