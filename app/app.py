from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import PostCreate, PostResponse, UserRead, UserCreate, UserUpdate
from app.db import Post, create_db_and_tables, get_async_session, User
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
import shutil
import os
import uuid
import tempfile
import aiofiles
from app.users import auth_backend, current_active_user, fastapi_users

@asynccontextmanager
async def lifespan(app: FastAPI):
  await create_db_and_tables()
  yield

app = FastAPI(lifespan=lifespan)

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix='/auth/jwt', tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix='/auth', tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix='/auth', tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix='/auth', tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix='/users', tags=["users"])


# @app.post("/upload")
# async def upload_file(
#     file: UploadFile = File(...),
#     caption: str = Form(...),
#     user: User = Depends(current_active_user),
#     session: AsyncSession = Depends(get_async_session)
# ):
#     MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
#     ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webm", "video/mp4"}
    
#     # Validate file type
#     if file.content_type not in ALLOWED_TYPES:
#         raise HTTPException(415, "Unsupported file type")
    
#     # Validate file size
#     file.file.seek(0, 2)
#     size = file.file.tell()
#     file.file.seek(0)
#     if size > MAX_FILE_SIZE:
#         raise HTTPException(413, "File too large")
    
#     temp_file_path = None
#     try:
#         # Async file save
#         suffix = os.path.splitext(file.filename)[1]
#         temp_file_path = f"/tmp/{uuid.uuid4()}{suffix}"
        
#         async with aiofiles.open(temp_file_path, "wb") as f:
#             async for chunk in file.file:
#                 await f.write(chunk)
        
#         # Upload to ImageKit
#         async with aiofiles.open(temp_file_path, "rb") as f:
#             upload_result = imagekit.files.upload(
#                 file=f, 
#                 file_name=file.filename,
#                 tags=["backend-upload"]
#             )
        
#         # Save to DB
#         post = Post(
#             user_id=user.id,
#             caption=caption,
#             url=upload_result.url,
#             file_type="video" if file.content_type.startswith("video/") else "image",
#             file_name=file.filename
#         )
#         session.add(post)
#         await session.commit()
#         await session.refresh(post)
#         return post
    
#     except Exception as e:
#         raise HTTPException(500, str(e))
#     finally:
#         if temp_file_path and os.path.exists(temp_file_path):
#             os.unlink(temp_file_path)
#         await file.close()


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(...),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    print(f"🔍 UPLOAD START: {file.filename} ({file.content_type}) by user {user.id}")
    
    # Skip validation for debug
    temp_file_path = None
    try:
        # Create temp file (Windows compatible)
        suffix = os.path.splitext(file.filename)[1]
        temp_file_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}{suffix}")
        print(f"📁 Temp file: {temp_file_path}")
        
        # Save file synchronously for now (your original worked)
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        print("✅ Temp file created, now uploading to ImageKit...")
        
        # Test ImageKit upload
        with open(temp_file_path, "rb") as f:  # Sync open for ImageKit
            upload_result = imagekit.files.upload(
                file=f,
                file_name=file.filename,
                tags=["backend-upload"]
            )
        
        print(f"✅ ImageKit SUCCESS: {upload_result.url}")
        
        # Save to DB
        post = Post(
            user_id=user.id,
            caption=caption,
            url=upload_result.url,
            file_type="video" if file.content_type.startswith("video/") else "image",
            file_name=file.filename
        )
        session.add(post)
        await session.commit()
        await session.refresh(post)
        print("✅ DB saved!")
        return post
        
    except Exception as e:
        print(f"❌ UPLOAD ERROR: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        await file.close()



@app.get("/feed")
async def get_feed(
   session: AsyncSession = Depends(get_async_session),
   user: User = Depends(current_active_user),
): 
  result = await session.execute(select(Post).order_by(Post.created_at.desc()))
  posts = [row[0] for row in result.all()]
  
  result = await session.execute(select(User))
  users = [row[0] for row in result.all()]
  user_dict = {u.id: u.email for u in users}

  posts_data = []
  for post in posts:
     posts_data.append(
        {
           "id": str(post.id),
           "user_id": str(post.user_id),
           "caption": post.caption,
           "url": post.url,
           "file_type": post.file_type,
            "file_name": post.file_name,
            "created_at": post.created_at.isoformat(),
            "is_owner": post.user_id == user.id,
            "email": user_dict.get(post.user_id, "unknown"
            )
        }
     )


  return {"posts": posts_data}


@app.delete("/posts/{post_id}")
async def delete_post(
   post_id: str,
   session: AsyncSession = Depends(get_async_session),
   user: User = Depends(current_active_user),
):
   try:
      post_uuid = uuid.UUID(post_id)
      result = await session.execute(select(Post).where(Post.id == post_uuid))
      post = result.scalars().first()
      if not post:
         raise HTTPException(status_code=404, detail="Post not found")
      
      if post.user_id != user.id:
         raise HTTPException(status_code=403, detail="You don't have permission to delete this post")

      await session.delete(post)
      await session.commit()
      return {"success": True, "message": "Post deleted successfully"}
   except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))