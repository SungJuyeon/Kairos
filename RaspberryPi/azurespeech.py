import logging
import azure.cognitiveservices.speech as speechsdk

class AzureSpeech:
    def __init__(self):
        self.azure_speech_key = "dbcff10c6d064f46879abce959e5b1d3"
        self.azure_service_region = "3d7bf8e47ce548a7ba100245c6de2e2e"
        self.answer_text = ""

    def tts(self):
        """
        Azure Speech Service를 이용해 Text-to-Speech
        """
        speech_key = self.azure_speech_key
        service_region = self.azure_service_region

        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_config.speech_synthesis_voice_name = "ko-KR-SeoHyeonNeural"

        if not self.answer_text:
            text = "오류가 발생했어요. 문제가 계속된다면 관리자에게 문의하세요."
            logging.error("TTS API 실행 전 Answer Text Result가 비어있습니다.")
        else:
            text = self.answer_text

        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

        result = speech_synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logging.info(f"TTS Speech synthesized for text [{text}]")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            logging.error(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                logging.error(f"TTS Error details: {cancellation_details.error_details}")