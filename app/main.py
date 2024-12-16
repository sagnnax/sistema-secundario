from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from config.database  import engine, Base
import routes.paciente_route, routes.expediente_route
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.title = "Sistema - Secundario"
app.version = "1.0"

@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")

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