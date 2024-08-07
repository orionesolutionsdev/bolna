import time
from .base_manager import BaseManager
from .task_manager import TaskManager
from datetime import datetime
from bolna.helpers.logger_config import configure_logger
from bolna.models import AGENT_WELCOME_MESSAGE
from bolna.helpers.utils import update_prompt_with_context
from twilio.rest import Client
import requests
import boto3
import tempfile
import os

from pymongo import MongoClient
import os

logger = configure_logger(__name__)
RECORDING_BUCKET_NAME = os.getenv("RECORDING_BUCKET_NAME")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


def mongodb_connection():
    """
    Establishes a connection to the MongoDB database using the environment variables 'MONGO_URL' and 'MONGO_DATABASE'.
    """
    try:
        mongo_client = MongoClient(os.getenv('MONGODB_URI'))
        db = mongo_client[os.getenv('MONGO_DATABASE')]
    except ValueError as e:
        raise ValueError(f"Error in mongodb_connection: {e.args[0]}")
    return db


def twilio_client():
    tw_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    return tw_client


def boto_client():
    try:
        s3_client = boto3.client(
            "s3",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        return s3_client
    except:
        print("Exception in bot_client")


def download_and_upload_to_s3(call_sid):
    try:
        # Create a temporary file to store the recording
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_file:
            temp_file_name = temp_file.name

            # Download the recording
            client = twilio_client()
            recordings = client.recordings.list(call_sid=call_sid)
            for recording in recordings:
                recording_url = (
                    f"https://api.twilio.com{recording.uri.replace('.json', '.wav')}"
                )
                print(f"Recording URL: {recording_url}")
                recording_content = requests.get(
                    recording_url, auth=(client.username, client.password)
                ).content
                temp_file.write(recording_content)
                print(
                    f"Recording downloaded and saved to temporary file {temp_file_name}"
                )

            # Upload the temporary file to S3
            s3_client = boto_client()
            s3_object_name = f"recordings/{call_sid}.wav"
            s3_client.upload_file(temp_file_name, RECORDING_BUCKET_NAME, s3_object_name)
            s3_file_path = os.path.join("s3://mybot-development/", s3_object_name)
            # print(f"Uploaded {temp_file_name} to S3 bucket {settings.s3_bucket_name} as {s3_object_name}")

            return s3_file_path

    except Exception as e:
        print(f"Error downloading/uploading recordings: {str(e)}")


db = mongodb_connection()


class AssistantManager(BaseManager):
    def __init__(self, agent_config, ws=None, assistant_id=None, context_data=None, conversation_history=None,
                 turn_based_conversation=None, cache=None, input_queue=None, output_queue=None, **kwargs):
        super().__init__()
        self.tools = {}
        self.websocket = ws
        self.agent_config = agent_config
        self.context_data = context_data
        self.tasks = agent_config.get('tasks', [])
        self.task_states = [False] * len(self.tasks)
        self.assistant_id = assistant_id
        self.run_id = f"{self.assistant_id}#{str(int(time.time() * 1000))}"
        self.turn_based_conversation = turn_based_conversation
        self.cache = cache
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.kwargs = kwargs
        self.conversation_history = conversation_history
        self.kwargs['agent_welcome_message'] = update_prompt_with_context(agent_config.get('agent_welcome_message', AGENT_WELCOME_MESSAGE), context_data)

    async def run(self, local=False, run_id=None):
        """
        Run will start all tasks in sequential format
        """
        if run_id:
            self.run_id = run_id
        result = {}
        input_parameters = None
        for task_id, task in enumerate(self.tasks):
            logger.info(
                f"Running task {task_id} {task} and sending kwargs {self.kwargs}"
            )
            task_manager = TaskManager(
                self.agent_config.get(
                    "agent_name", self.agent_config.get("assistant_name")
                ),
                task_id,
                task,
                self.websocket,
                context_data=self.context_data,
                input_parameters=input_parameters,
                assistant_id=self.assistant_id,
                run_id=self.run_id,
                turn_based_conversation=self.turn_based_conversation,
                                       cache=self.cache, input_queue=self.input_queue, output_queue=self.output_queue,
                                       conversation_history=self.conversation_history, **self.kwargs)
            await task_manager.load_prompt(self.agent_config.get("agent_name", self.agent_config.get("assistant_name")),
                                           task_id, local=local, **self.kwargs)
            task_output = await task_manager.run()
            task_output["run_id"] = self.run_id
            yield task_id, task_output.copy()
            self.task_states[task_id] = True
            if task_id == 0:
                input_parameters = task_output

                # removing context_data from non-conversational tasks
                self.context_data = None
            logger.info(f"task_output {task_output}")
            if task["task_type"] == "conversation":
                result = task_output.copy()
                result['agent_id'] = task_manager.assistant_id
                result['created_at'] = datetime.now().isoformat()
                result['model'] = task_manager.task_config["tools_config"]["llm_agent"]["model"]
                result['temperature'] = task_manager.task_config["tools_config"]["llm_agent"]["temperature"]
                result['max_tokens'] = task_manager.task_config["tools_config"]["llm_agent"]["max_tokens"]
                result['synthesizer_voice'] = task_manager.synthesizer_voice
                result['synthesizer_provider'] = task_manager.synthesizer_provider
            if task["task_type"] == "summarization":
                result['summarised_data']  = task_manager.summarized_data
            if task["task_type"] == "extraction":
                extracted_data =  task_output["extracted_data"]
                result["extracted_data"] = extracted_data
                input_parameters["extraction_details"] = result
        if result and result.get("call_sid", None):
            result["recording_path"] = download_and_upload_to_s3(result.get("call_sid", None))
        logger.info("Updating Execution Information in MongoDB")
        db['execution_metadata'].insert_one(result)
        logger.info("Done Updating Execution Information in MongoDB")
        logger.info("Done with execution of the agent")
