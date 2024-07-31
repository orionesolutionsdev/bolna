from typing import List
from pydantic import BaseModel, field_validator
from bolna.models import Transcriber
from fastapi import APIRouter, HTTPException, Request
from vo_utils.database_utils import db
from config import settings
from vo_utils.clerk_auth_utils import get_user_id_from_Token
import datetime


router = APIRouter()

class WeekDayCallData(BaseModel):
    name: str
    inbound: int
    outbound: int

    @field_validator("name")
    def validate_name(cls, value):
        if value not in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            raise ValueError("Invalid week day name")
        return value

class CallDurationData(BaseModel):
    name: str
    average_duration: float

class DashBoardModel(BaseModel):
    total_calls: int
    average_call_duration: int
    total_agents: int
    week_data: List[WeekDayCallData]
    call_duration_data: List[CallDurationData]

    @field_validator("total_calls")
    def validate_total_calls(cls, value):
        if value < 0:
            raise ValueError("Total calls cannot be negative")
        return value
    
    @field_validator("average_call_duration")
    def validate_average_call_duration(cls, value):
        if value < 0:
            raise ValueError("Average call duration cannot be negative")
        return value
    
    @field_validator("total_agents")
    def validate_total_agents(cls, value):
        if value < 0:
            raise ValueError("Total agents cannot be negative")
        return value
    
    @field_validator("week_data")
    def validate_week_data(cls, value):
        if len(value) != 7:
            raise ValueError("Week data should have 7 entries")
        return value
    
    @field_validator("call_duration_data")
    def validate_call_duration_data(cls, value):
        if len(value) != 4:
            raise ValueError("Call duration data should have 4 entries")
        return value

@router.get("/dashboard", response_model=DashBoardModel)
def get_dashboard_data(
        header: Request,
):
    total_calls = 0
    average_call_duration = 0
    total_agents = 0
    week_data = [ WeekDayCallData(name="Mon", inbound=0, outbound=0),
                 WeekDayCallData(name="Tue", inbound=0, outbound=0),
                 WeekDayCallData(name="Wed", inbound=0, outbound=0),
                 WeekDayCallData(name="Thu", inbound=0, outbound=0),
                 WeekDayCallData(name="Fri", inbound=0, outbound=0),
                 WeekDayCallData(name="Sat", inbound=0, outbound=0),
                 WeekDayCallData(name="Sun", inbound=0, outbound=0)]
    call_duration_data = [CallDurationData(name="Week 1", average_duration=0),
                            CallDurationData(name="Week 2", average_duration=0),
                            CallDurationData(name="Week 3", average_duration=0),
                            CallDurationData(name="Week 4", average_duration=0)]
    user_id = get_user_id_from_Token(header)
    for doc in db[settings.MONGO_COLLECTION].find({"user_id": user_id}, {"agent_id": 1}):
        total_agents += 1
        execs = db[settings.EXECUTION_COLLECTION].find({"agent_id": doc["agent_id"]}, {'conversation_time': 1})
        for exec in execs:
            total_calls += 1
            average_call_duration += exec["conversation_time"]
        # Get date of Monday of the current week
        # Get the date of the current day
        today = datetime.datetime.now()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        monday = today - datetime.timedelta(days=today.weekday())
        # Get the date of the current day
        day = today.strftime("%a")
        print(day, monday, today)
        # 2024-07-30T12:43:45.723812
        # convert today and monday to the following format 2024-07-30T12:43:45.723812
        execs = db[settings.EXECUTION_COLLECTION].find({"agent_id": doc["agent_id"], "created_at": {"$gte": monday.strftime("%Y-%m-%dT%H:%M:%S.%f")}}, {"conversation_time": 1, "created_at": 1}).sort("created_at", 1)
        # print(list(execs))
        for i, data in enumerate(week_data):
            if data.name == day:
                for exec in execs:
                    print(exec)
                    created_at = datetime.datetime.strptime(exec["created_at"], "%Y-%m-%dT%H:%M:%S.%f")
                    if created_at >= monday and created_at < monday + datetime.timedelta(days=1 + i):
                        data.outbound += 1
                break
        
            
        date_4_weeks_ago = monday - datetime.timedelta(days=21)
        for week in call_duration_data:
            num_calls = 0
            execs = db[settings.EXECUTION_COLLECTION].find({"agent_id": doc["agent_id"], "created_at": {"$gte": date_4_weeks_ago.strftime("%Y-%m-%dT%H:%M:%S.%f"), "$lt": (date_4_weeks_ago + datetime.timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S.%f")}}, {"conversation_time": 1, "created_at": 1})
            for exec in execs:
                num_calls += 1
                created_at = datetime.datetime.strptime(exec["created_at"], "%Y-%m-%dT%H:%M:%S.%f")
                if created_at >= date_4_weeks_ago and created_at < date_4_weeks_ago + datetime.timedelta(days=7):
                    week.average_duration += exec["conversation_time"]
            if num_calls > 0:
                week.average_duration = week.average_duration // num_calls
            date_4_weeks_ago += datetime.timedelta(days=7)

    if total_calls > 0:
        average_call_duration = average_call_duration // total_calls
    dbm= DashBoardModel(
        total_calls=total_calls,
        average_call_duration=average_call_duration,
        total_agents=total_agents,
        week_data=week_data,
        call_duration_data=call_duration_data
    )
    return dbm



            


    
        