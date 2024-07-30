import boto3
import os
import dotenv
import azure.cognitiveservices.speech as speechsdk


agents_polly = {"Raveena": "standard",
          "Joey": "neural",
          "Emma": "neural",
          "Niamh": "neural",
          "Danielle": "neural",
          "Arthur": "neural"}

agents_azure = {"Sonia": "en-GB-SoniaNeural",
            "Ryan": "en-GB-RyanNeural",
            "Neerja": "en-IN-NeerjaNeural",
            "Ava": "en-US-AvaNeural",
            "Andrew": "en-US-AndrewNeural"}

dotenv.load_dotenv("local_setup/.env")
polly_client = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
).client('polly')
text = "Hi, This is AI Agent, How can I help you?"

def dowload_sample_voices_polly(agents=agents_polly, folder="../"):
    for agent_name, engine in agents.items():
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId=agent_name,
            Engine=engine
        )

        with open(f'{folder}{agent_name}.mp3', 'wb') as file:
            file.write(response['AudioStream'].read())

        print(f"Audio file saved as {folder}{agent_name}.mp3")


def dowload_sample_voices_azure(agents=agents_azure, folder="../"):
    if os.getenv('AZURE_SPEECH_KEY') is None or os.getenv('AZURE_SPEECH_REGION') is not None:
        speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('AZURE_SPEECH_KEY'), region=os.environ.get('AZURE_SPEECH_REGION'))
        for agent_name, engine in agents.items():
            speech_config.speech_synthesis_voice_name=engine
            audio_config = speechsdk.audio.AudioOutputConfig(filename=f"{folder}{agent_name}.wav")
            speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
            speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

            if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print("Speech synthesized for text [{}]".format(text))
            elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speech_synthesis_result.cancellation_details
                print("Speech synthesis canceled: {}".format(cancellation_details.reason))
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    if cancellation_details.error_details:
                        print("Error details: {}".format(cancellation_details.error_details))
                        print("Did you set the speech resource key and region values?")








if __name__ == "__main__":
    dowload_sample_voices_polly()
    dowload_sample_voices_azure()

