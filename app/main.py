from fastapi import FastAPI
from config.database  import engine, Base
import routes.paciente_route, routes.expediente_route
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.title = "Sistema - Secundario"
app.version = "1.0"

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
        
app.include_router(routes.paciente_route.router)
app.include_router(routes.expediente_route.router)