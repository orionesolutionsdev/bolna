from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
from vo_utils.database_utils import db, async_db
from config import settings
import csv
from datetime import datetime, timezone
import asyncio
import httpx
import requests

router = APIRouter()


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
async def schedule_task(batch_id: str = Form(...), scheduled_at: datetime = Form(...)):
    # Calculate the delay until the scheduled_at datetime
    current_time = datetime.now(timezone.utc)
    # delay = (scheduled_at - current_time).total_seconds()
    delay = 10
    if delay <= 0:
        raise HTTPException(
            status_code=400, detail="Scheduled time must be in the future"
        )
    
    print(delay)
    # Fetch data from MongoDB based on batch_id
    tasks_cursor = db[settings.BATCH_COLLECTION].find({"batch_id": batch_id})


    for task in list(tasks_cursor):
        phone_number = task.get("recipient_phone_number")
        username = task.get("username")
        agent_id = task.get("agent_id")
        print(phone_number)
        print(username)
        print(agent_id)
        # Schedule the task asynchronously
        # await asyncio.sleep(delay)
        process_task(agent_id, phone_number, username)
        # asyncio.create_task(process_task(agent_id, phone_number, username))

    # return JSONResponse(content={"message": "success", "state": "scheduled"})


async def process_task(agent_id, recipient_phone_number, username):
    # Simulate making API calls or any other task processing
    async with httpx.AsyncClient() as client:

        # Example of making a POST request to an API endpoint
        url = app_callback_url + "/call"
        payload = {
            "agent_id": agent_id,
            "recipient_phone_number": recipient_phone_number,
            "recipient_data": {"username": username},
        }
        print(payload)
        print(url)
        # response = await client.post(url, json=payload)
        # print(
        #     f"API call result for {recipient_phone_number}: {response.status_code}"
        # )
        await asyncio.sleep(3)

