from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
import csv
from datetime import datetime
import requests
from config import settings
from vo_utils.clerk_auth_utils import get_user_id_from_Token
from vo_utils.database_utils import db
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from config import settings
from typing import Optional

scheduler = BackgroundScheduler()
scheduler.start()
router = APIRouter()


class Contact(BaseModel):
    recipient_phone_number: str
    username: str


class batch_model(BaseModel):
    batch_id: str
    scheduled_at: Optional[datetime] = None
    delay_bw_call: Optional[int] = 300


@router.post("/batches")
async def create_batch(
    header: Request,
    agent_id: str = Form(...),
    file: UploadFile = File(...),
    batch_name="Default",
    from_number=settings.from_number,
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="File format not supported. Please upload a CSV file.",
        )

    # Read the CSV file
    content = await file.read()
    content = content.decode("utf-8").splitlines()
    csv_reader = csv.DictReader(content)

    # Validate CSV content
    required_columns = {"recipient_phone_number", "username"}
    if not required_columns.issubset(csv_reader.fieldnames):
        raise HTTPException(
            status_code=400, detail="CSV file is missing required columns."
        )

    # Generate unique batch_id
    batch_id = str(uuid.uuid4())
    user_id = get_user_id_from_Token(header)

    # Prepare data for MongoDB
    batch_data = {}
    user_data = []
    queue_result = []
    for row in csv_reader:
        queue_id = str(uuid.uuid4())

        contact = {
            "recipient_phone_number": row["recipient_phone_number"],
            "username": row["username"],
            "queue_id": queue_id,
        }
        call_queue = {
            "agent_id": agent_id,
            "batch_id": batch_id,
            "queue_id": queue_id,
            "user_id": user_id,
            "batch_name": batch_name,
            "created_at": datetime.now().isoformat(),
            "phone_number": row["recipient_phone_number"],
            "username": row["username"],
            "status": "pending",
        }

        user_data.append(contact)
        queue_result.append(call_queue)
    batch_data["user_id"] = user_id
    batch_data["agent_id"] = agent_id
    batch_data["batch_name"] = batch_name
    batch_data["batch_id"] = batch_id
    batch_data["from_number"] = from_number
    batch_data["user_data"] = user_data
    batch_data["batch_status"] = "pending"
    batch_data["created_at"] = datetime.now().isoformat()
    # Insert data into MongoDB
    db[settings.BATCH_COLLECTION].insert_one(batch_data)
    db[settings.CALL_QUEUE].insert_many(queue_result)
    return JSONResponse(
        content={
            "batch_id": batch_id,
            "batch_name": batch_name,
            "batch_status": "pending",
            "message": "Batch created successfully",
        }
    )


@router.get("/batches")
async def get_batches(header: Request):
    user_id = get_user_id_from_Token(header)
    batches = list(
        db[settings.BATCH_COLLECTION]
        .find({"user_id": user_id}, {"_id": 0})
        .sort("created_at", -1)
    )
    return JSONResponse(content=batches, status_code=200)


@router.get("/queues")
async def get_call_queues(header: Request):
    user_id = get_user_id_from_Token(header)
    batches = list(
        db[settings.CALL_QUEUE]
        .find({"user_id": user_id}, {"_id": 0})
        .sort("created_at", -1)
    )
    return JSONResponse(content=batches, status_code=200)


def scheduled_task(payload, queue_id):
    filter = {"queue_id": queue_id}
    update = {"$set": {"status": "progress"}}
    db[settings.CALL_QUEUE].update_one(filter, update)
    response = requests.post(settings.CALL_URL, json=payload
    )
    if response.status_code == 200:
        update = {"$set": {"status": "completed"}}
        db[settings.CALL_QUEUE].update_one(filter, update)
    else:
        update = {"$set": {"status": "failed"}}
        db[settings.CALL_QUEUE].update_one(filter, update)


@router.get("/stop_all_tasks")
async def stop_all_tasks():
    scheduler.remove_all_jobs()
    return {"message": "All tasks have been stopped successfully."}


@router.post("/schedule_batch")
def schedule_message(batch_model: batch_model):
    filter = {"batch_id": batch_model.batch_id}
    update = {"$set": {"batch_status": "progress"}}
    batch_data = db[settings.BATCH_COLLECTION].find_one(filter)
    if batch_data:
        scheduled_at = batch_model.scheduled_at
        if scheduled_at and scheduled_at < datetime.now():
            raise HTTPException(status_code=400, detail="Scheduled time must be in the future")
        db[settings.BATCH_COLLECTION].update_one(filter, update)
        agent_id = batch_data.get("agent_id")
        user_data = batch_data.get("user_data")
        for user in user_data:
            payload = {
                "agent_id": agent_id,
                "recipient_phone_number": user.get("recipient_phone_number"),
                "recipient_data": {"username": user.get("username")},
            }
            queue_id = user.get("queue_id")
            scheduler.add_job(
                scheduled_task, "date", run_date=scheduled_at, args=[payload, queue_id]
            )
            scheduled_at += timedelta(seconds=batch_model.delay_bw_call)
    else:
        batch_data = []
        return {"message": "Batch not found"}
    return {"message": "Batch will be scheduled to run in the background"}
