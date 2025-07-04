from kokoro import KPipeline
import soundfile as sf
import numpy as np
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

def split_text(text):
    chunks = re.split(r'(?<=[।.!?])\s*', text)
    return [c.strip() for c in chunks if c.strip()]

def concat_audio(audio_chunks):
    return np.concatenate(audio_chunks)

def synthesize_chunk(chunk, voice="hm_omega", speed=1.3):
    # Create a pipeline per thread (safer)
    pipeline = KPipeline(lang_code="hi")
    for _, _, audio in pipeline(chunk, voice=voice, speed=speed):
        return audio  # Return audio for this chunk

def generate_natural_speech_parallel(text, voice="hm_omega", output_file="output_natural.wav"):
    chunks = split_text(text)
    print(f"Split into {len(chunks)} chunks")

    audio_chunks = []
    with ThreadPoolExecutor(max_workers=4) as executor:  # Adjust number of workers per your CPU cores
        futures = {executor.submit(synthesize_chunk, chunk, voice): i for i, chunk in enumerate(chunks)}
        
        # Collect results in order of chunk index for proper concatenation
        results = [None] * len(chunks)
        for future in as_completed(futures):
            idx = futures[future]
            audio = future.result()
            results[idx] = audio

    final_audio = concat_audio(results)
    sf.write(output_file, final_audio, samplerate=24000)
    print(f"\n✅ Saved parallel synthesized audio to '{output_file}'")

if __name__ == "__main__":
    sample_text = (
        "नमस्ते! मैं आपका सहायक हूँ। "
        "कृपया अपना नाम बताइए। "
        "मैं आपकी सहायता करने के लिए तैयार हूँ। "
        "क्या आप कॉलेज की जानकारी चाहते हैं?"
    )
    generate_natural_speech_parallel(sample_text)
