from transformers import *
import torch
import torchaudio
import textwrap

class SoundToText:
    pipe: AutomaticSpeechRecognitionPipeline | None = None

    def load_model(self) -> None:
        if torch.cuda.is_available():
            device = "cuda:0"
        elif torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"
        
        pipe = pipeline("automatic-speech-recognition", model="openai/whisper-medium.en", device=device)
        self.pipe = pipe
        
    def get_transcription_whisper(self, audio_path, return_timestamps=True, chunk_length_s=10, stride_length_s=2):
        if not self.pipe:
            raise RuntimeError("Pipeline is not loaded")
        res = self.pipe(self.load_audio(audio_path), return_timestamps=return_timestamps,
                            chunk_length_s=chunk_length_s, stride_length_s=stride_length_s)
        return self.wrap(res["text"])
    
    def load_audio(self, audio_path):
        speech, sr = torchaudio.load(audio_path)
        resampler = torchaudio.transforms.Resample(sr, 16000)
        speech = resampler(speech).squeeze()
        speech = speech.numpy()
        num_channels, num_frames = speech.shape
        if num_channels == 1:
            return speech
        else:
            return speech[0]
    
    def wrap(self, x):
        return textwrap.fill(x, replace_whitespace = False, fix_sentence_endings = True)
    


