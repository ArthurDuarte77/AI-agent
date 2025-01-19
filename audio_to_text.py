import os
import requests
from google.cloud import speech_v1 as speech
from google.oauth2 import service_account
import tempfile
import ffmpeg


def audio_to_text(audio_url, credentials_path):
    """
    Transcribes audio from a given URL to text using Google Cloud Speech-to-Text.
    Handles audio format conversion using ffmpeg.

    Args:
        audio_url (str): The URL of the audio file.
        credentials_path (str): The path to your Google Cloud service account JSON key file.

    Returns:
        str: The transcribed text, or None if transcription fails.
    """

    try:
        # Download the audio from the URL
        response = requests.get(audio_url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Create a temporary file to save audio data
        with tempfile.NamedTemporaryFile(delete=False, suffix=".oga") as tmp_oga_file:
            for chunk in response.iter_content(chunk_size=8192):
                tmp_oga_file.write(chunk)
            temp_oga_file_name = tmp_oga_file.name

         # Create a temporary file for the WAV output
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav_file:
            temp_wav_file_name = tmp_wav_file.name
            
        # Use ffmpeg to convert the downloaded .oga to .wav (LINEAR16)
        try:
            ffmpeg.input(temp_oga_file_name).output(
                temp_wav_file_name,
                format='wav',
                acodec='pcm_s16le',  # Linear PCM 16-bit little endian
                ar=44100 #adjust based on your audio.
            ).run(overwrite_output=True)
        except ffmpeg.Error as e:
             print(f"Error during audio conversion: {e.stderr.decode()}")
             return None
           
        # Create Google Cloud Speech client
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        client = speech.SpeechClient(credentials=credentials)

        # Prepare audio config
        audio_config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,  # Or WAV depending on what is output by ffmpeg, this should be LINEAR16
            sample_rate_hertz=44100,  # Adjust based on your audio.
            language_code="en-US",  # Adjust based on audio language
        )

        # Prepare the audio data
        with open(temp_wav_file_name, "rb") as f:
             audio_content = f.read()
        audio = speech.RecognitionAudio(content=audio_content)
        

        # Perform the transcription
        response = client.recognize(config=audio_config, audio=audio)

        # Process the transcription results
        transcribed_text = ""
        for result in response.results:
            transcribed_text += result.alternatives[0].transcript + " "


    except requests.exceptions.RequestException as e:
            print(f"Error downloading audio: {e}")
            transcribed_text = None
    except Exception as e:
        print(f"Error during transcription: {e}")
        transcribed_text = None
    finally:
        #Clean up the temporary file if created
        if 'temp_oga_file_name' in locals():
            os.remove(temp_oga_file_name)
        if 'temp_wav_file_name' in locals():
            os.remove(temp_wav_file_name)
    return transcribed_text


if __name__ == '__main__':
    # Replace with a valid audio file URL
    audio_url = "http://134.122.29.170:3000/api/files/default/true_553791332517@c.us_21CC1AF89AB27DF2A694EDE127CEA6CA_out.oga"

    # Replace with the path to your service account key file
    credentials_path = "esp8266-352723-72e082175c46.json" # Replace with your key
    
    transcription = audio_to_text(audio_url, credentials_path)

    if transcription:
        print("Transcription:\n", transcription)
    else:
        print("Transcription failed.")