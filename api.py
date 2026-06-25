import base64
import os
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from mnemo.db import sqlite as db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ArtifactPayload(BaseModel):
    markdown: str
    images: list[str]
    datetime: str
    quadrant: str
    weekCharacter: str
    timeCharacter: str
    dayTheme: str
    manual: bool

@app.post("/ingest")
def ingest_artifact(payload: ArtifactPayload):
    try:
        db.init_db()
        # Create a new session for this inbox submission
        session_id = db.create_session(
            title=f"Inbox Submission - {payload.datetime}", 
            category="Inbox"
        )
        
        # Save raw artifact
        artifact_id = db.save_raw_artifact(
            session_id=session_id,
            title=f"Artifact {payload.datetime}",
            markdown=payload.markdown,
            source_screenshot_count=len(payload.images),
            week_character=payload.weekCharacter,
            day_theme=payload.dayTheme,
            time_character=payload.timeCharacter,
        )
        
        # Process base64 images
        images_dir = Path("screenshots")
        images_dir.mkdir(exist_ok=True)
        
        for b64_str in payload.images:
            # strip data url prefix if present
            if "," in b64_str:
                b64_str = b64_str.split(",")[1]
            img_data = base64.b64decode(b64_str)
            filepath = images_dir / f"artifact_{artifact_id}_{uuid.uuid4().hex[:8]}.png"
            with open(filepath, "wb") as f:
                f.write(img_data)
            db.save_artifact_image(artifact_id, str(filepath))
            
        return {"status": "success", "artifact_id": artifact_id}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)
