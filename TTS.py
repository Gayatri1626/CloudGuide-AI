from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# IBM Watson Text to Speech API setup
API_KEY = "QpC9mcDKM6AaEV30x5FEwQDkCnYIcP2FiL7QT33sA7yP"
SERVICE_URL = "https://api.au-syd.text-to-speech.watson.cloud.ibm.com/instances/25049ac3-565d-41da-8d8b-6dc40281b597"

authenticator = IAMAuthenticator(API_KEY)
text_to_speech = TextToSpeechV1(authenticator=authenticator)
text_to_speech.set_service_url(SERVICE_URL)

def generate_audio_stream(text):
    """
    Generate an audio stream from text using IBM Watson Text to Speech.
    """
    try:
        response = text_to_speech.synthesize(
            text=text,
            voice='en-US_AllisonV3Voice',
            accept='audio/mp3'
        ).get_result()
        return response.content
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None
