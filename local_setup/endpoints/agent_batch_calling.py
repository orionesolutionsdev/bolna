from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
from vo_utils.database_utils import db, async_db
from config import settings
import csv
from datetime import datetime, timezone
import asyncio
import requests
import time

router = APIRouter()

schedule_start_seconds = 5
gap_bw_call_seconds = 60
task_queue = asyncio.Queue()


class Contact(BaseModel):
    recipient_phone_number: str
    username: str


def get_app_callback_url():
    response = requests.get("http://ngrok:4040/api/tunnels")  # ngrok interface
    app_callback_url = None
    if response.status_code == 200:
        data = response.json()
        for tunnel in data["tunnels"]:
            if tunnel["name"] == "twilio-app":
                app_callback_url = tunnel["public_url"]

        return app_callback_url
    else:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")


app_callback_url = get_app_callback_url()


@router.on_event("startup")
async def startup_event():
    # Start the worker coroutine
    asyncio.create_task(process_task(schedule_start_seconds))


@router.post("/batches")
async def create_batch(agent_id: str = Form(...), file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="File format not supported. Please upload a CSV file.",
        )

    # Read the CSV file
    content = await file.read()
    content = content.decode("utf-8").splitlines()
    print(content)
    csv_reader = csv.DictReader(content)

    # Validate CSV content
    required_columns = {"recipient_phone_number", "username"}
    if not required_columns.issubset(csv_reader.fieldnames):
        raise HTTPException(
            status_code=400, detail="CSV file is missing required columns."
        )

    # Generate unique batch_id
    batch_id = str(uuid.uuid4())

    # Prepare data for MongoDB
    contacts = []
    for row in csv_reader:
        contact = {
            "batch_id": batch_id,
            "agent_id": agent_id,
            "recipient_phone_number": row["recipient_phone_number"],
            "username": row["username"],
        }
        contacts.append(contact)

    # Insert data into MongoDB
    db[settings.BATCH_COLLECTION].insert_many(contacts)

    return JSONResponse(
        content={
            "batch_id": batch_id,
            "status": "success",
            "message": "Batch created successfully",
        }
    )


@router.post("/batches/schedule")
async def schedule_task(batch_id: str = Form(...), schedule_seconds: int =30):
    global schedule_start_seconds
    schedule_start_seconds = schedule_seconds  # Update schedule_seconds globally
    tasks_cursor = db[settings.BATCH_COLLECTION].find({"batch_id": batch_id})
    for task in list(tasks_cursor)[:2]:
        phone_number = task.get("recipient_phone_number")
        username = task.get("username")
        agent_id = task.get("agent_id")
        await task_queue.put((agent_id, phone_number, username))
    return JSONResponse(content={"message": "success", "state": "scheduled"})


async def process_task(schedule_start_seconds):
    await asyncio.sleep(schedule_start_seconds)
    while True:
        agent_id, phone_number, username = await task_queue.get()
        print(f"Processing task for agent_id: {agent_id}, phone_number: {phone_number}, username: {username}")
        try:
            print(f"Processing task for agent_id: {agent_id}, phone_number: {phone_number}, username: {username}")
            url = app_callback_url+ "/call"
            print(url)
            payload = {
                "agent_id": agent_id,
                "recipient_phone_number": phone_number,
                "recipient_data": {"username": username},
            }
            response = requests.post(url, json=payload)

            # async with httpx.AsyncClient() as client:
                # response = await client.post(url, json=payload)
            print(f"API call result for {phone_number}: {response.status_code}")
            time.sleep(gap_bw_call_seconds)
        finally:
            task_queue.task_done()

