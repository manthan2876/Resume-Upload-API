import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from typing import List
from models import User, UserCreate, Employer, Employee

app = FastAPI(title="Kenexai Backend API")

# In-memory storage for demonstration purposes
# In a real application, you would use a database
users_db = []
user_id_counter = 1

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.get("/")
def read_root():
    return {"message": "Welcome to Kenexai Hackathon Backend API"}

# --- User REST API ---

@app.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    global user_id_counter
    new_user = {
        "id": user_id_counter,
        **user.model_dump()
    }
    users_db.append(new_user)
    user_id_counter += 1
    return new_user

@app.get("/users/", response_model=List[User])
def get_users():
    return users_db

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

# --- Resume PDF Upload API ---

@app.post("/upload-resume/", status_code=status.HTTP_201_CREATED)
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )
    
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": os.path.getsize(file_path),
        "message": "Resume uploaded successfully"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
