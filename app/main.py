from fastapi import FastAPI
from routers import emails
from dependencies.doc.doc import generate_documentation
import uvicorn
import socket  
hostname=socket.gethostname()   
IPAddr=socket.gethostbyname(hostname)

app = FastAPI(
    description= """MICROSERVICE FOR EMAIL OPERATIONS."""
)
app.include_router(
    emails.router
)

if __name__ == '__main__':
    generate_documentation(app)
    uvicorn.run(app, host=IPAddr, port=8000)