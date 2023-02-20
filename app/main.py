from fastapi import FastAPI
from routers import emails
from dependencies.doc.doc import generate_documentation, json_to_md
import uvicorn
import socket  
hostname=socket.gethostname()   
IPAddr=socket.gethostbyname(hostname)

app = FastAPI(
    docs_url=None,
    redoc_url='/docs',
    description= """
    MICROSERVICE FOR EMAIL OPERATIONS.
    """.upper()
)
app.include_router(
    emails.router
)

if __name__ == '__main__':
    generate_documentation(app)
    uvicorn.run(app, host=IPAddr, port=8000)