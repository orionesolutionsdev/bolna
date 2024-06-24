import os
import json
import requests
import uuid
from dotenv import load_dotenv
import redis.asyncio as redis
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from datetime import datetime
from config import settings
from vo_utils.database_utils import db
import plivo

app = FastAPI()
load_dotenv()
port = 8002

plivo_auth_id = os.getenv('PLIVO_AUTH_ID')
plivo_auth_token = os.getenv('PLIVO_AUTH_TOKEN')
plivo_phone_number = os.getenv('PLIVO_PHONE_NUMBER')

# Initialize Plivo client
plivo_client = plivo.RestClient(os.getenv('PLIVO_AUTH_ID'), os.getenv('PLIVO_AUTH_TOKEN'))


def populate_ngrok_tunnels():
    response = requests.get("http://ngrok:4040/api/tunnels")  # ngrok interface
    app_callback_url, websocket_url = None, None

    if response.status_code == 200:
        data = response.json()

        for tunnel in data['tunnels']:
            if tunnel['name'] == 'plivo-app':
                app_callback_url = tunnel['public_url']
            elif tunnel['name'] == 'bolna-app':
                websocket_url = tunnel['public_url'].replace('https:', 'wss:')

        return app_callback_url, websocket_url
    else:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")


@app.post('/call')
async def make_call(request: Request):
    try:
        call_details = await request.json()
        agent_id = call_details.get('agent_id', None)
        from_number = call_details.get('from_number', plivo_phone_number)
        recipient_data = call_details.get('recipient_data', None)
        context_id =  str(uuid.uuid4())
        data_for_db ={
                    'context_id': context_id,
                    'created_at': datetime.now().isoformat(),
                    'recipient_data': recipient_data
                    }
        db[settings.CALL_CONTEXTS].insert_one(data_for_db)

        if not agent_id:
            raise HTTPException(status_code=404, detail="Agent not provided")

        if not call_details or "recipient_phone_number" not in call_details:
            raise HTTPException(status_code=404, detail="Recipient phone number not provided")

        app_callback_url, websocket_url = populate_ngrok_tunnels()

        print(f'app_callback_url: {app_callback_url}')
        print(f'websocket_url: {websocket_url}')

        # adding hangup_url since plivo opens a 2nd websocket once the call is cut.
        # https://github.com/bolna-ai/bolna/issues/148#issuecomment-2127980509
        call = plivo_client.calls.create(
            from_=from_number,
            to_=call_details.get('recipient_phone_number'),
            answer_url=f"{app_callback_url}/plivo_callback?ws_url={websocket_url}&agent_id={agent_id}&context_id={context_id}",
            hangup_url=f"{app_callback_url}/plivo_hangup_callback",
            answer_method='POST')

        return PlainTextResponse("done", status_code=200)

    except Exception as e:
        print(f"Exception occurred in make_call: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post('/plivo_callback')
async def plivo_callback(request: Request, ws_url: str = Query(...), agent_id: str = Query(...), context_id: str = Query(...)):
    try:
        websocket_plivo_route = f'{ws_url}/chat/v1/{agent_id}/{context_id}'

        response = '''
        <Response>
            <Stream bidirectional="true">{}</Stream>
            <MultiPartyCall role="customer">mpc_name</MultiPartyCall>    
        </Response>
        '''.format(websocket_plivo_route)

        return PlainTextResponse(str(response), status_code=200, media_type='text/xml')

    except Exception as e:
        print(f"Exception occurred in plivo_callback: {e}")


@app.post('/plivo_hangup_callback')
async def plivo_hangup_callback(request: Request):
    # add any post call hangup processing
    return PlainTextResponse("", status_code=200)
