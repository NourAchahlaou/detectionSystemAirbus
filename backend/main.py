import os
from fastapi import  FastAPI
from fastapi.staticfiles import StaticFiles
from api.users.routes import user_routes  # Import API route definitions
from api.utils.database import get_db, initialize_roles
from api.camera.routes import camera_routes

from api.piece.routes import piece_routes
from database.inspection import InspectionImage
from detection.router import detection_router,identify_router
from oauth2 import oauth2_routes
from hardware.camera.camera import FrameSource
from database.defectDetectionDB import engine
from database.users import session , user,role,profile
from database.camera import camera_settings, camera
from database.piece import piece,piece_image
from fastapi.middleware.cors import CORSMiddleware
from hardware.camera import external_camera



app = FastAPI()

frame_source = FrameSource()


role.Base.metadata.create_all(bind=engine)
user.Base.metadata.create_all(bind=engine)
profile.Base.metadata.create_all(bind=engine)
session.Base.metadata.create_all(bind=engine)
camera.Base.metadata.create_all(bind=engine)
camera_settings.Base.metadata.create_all(bind=engine)
piece.Base.metadata.create_all(bind=engine)
piece_image.Base.metadata.create_all(bind=engine)
InspectionImage.Base.metadata.create_all(bind=engine)

# Initialize roles on application startup

@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    
    frame_source.detect_and_save_cameras(db)
   
    external_camera.get_usb_devices()
    initialize_roles(db)


# Serve static files from the "dataset" directory under the "/images" URL path
app.mount("/images", StaticFiles(directory="dataset"), name="images")

@app.get("/list-images")
def list_images():
    image_dir = "dataset"
    file_urls = []
    
    # Walk through all subdirectories and files
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            # Create the relative URL for each file
            relative_path = os.path.relpath(os.path.join(root, file), image_dir)
            file_urls.append(f"/images/{relative_path.replace(os.sep, '/')}")  # Ensure URL is formatted with forward slashes

    if file_urls:
        return {"files": file_urls}
    else:
        return {"error": "No files found"}
    

# Include API routers
app.include_router(user_routes.router, prefix="/users", tags=["users"])
# app.include_router(roles.router, prefix="/roles", tags=["roles"])
app.include_router(camera_routes.router, prefix="/cameras", tags=["cameras"])
app.include_router(oauth2_routes.router, prefix="", tags=["oauth"])
app.include_router(piece_routes.router,prefix="/piece",tags=["piece"])
app.include_router(detection_router.router,prefix="/detection",tags=["detection"])
app.include_router(identify_router.router,prefix="/identify",tags=["identify"])
# Allow CORS for your frontend app
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.on_event("shutdown")
async def shutdown_event():
    frame_source.stop()

@app.get("/")
def read_root():
    return {"message": "Welcome to Defect Detection System"}



if __name__ == "__main__":
    import uvicorn
    if os.getenv('ENVIRONMENT') == 'development':
        uvicorn.run(app, host="127.0.0.1", port=80000, reload=True)
    else :
        uvicorn.run(app, host="127.0.0.1", port=80000)





