from gtts import gTTS

def generate_voiceover(text, output_file="voiceover.mp3"):
    """
    Generate an AI voiceover from text.
    """
    print("🔊 Generating voiceover...")
    tts = gTTS(text, lang="en")
    tts.save(output_file)
    print(f"✅ Voiceover saved as {output_file}")

# import os
# from gtts import gTTS

# def generate_voiceover(text, output_file="voiceover.mp3"):
#     if os.path.exists(output_file):
#         print("🔊 Voiceover already exists.")
#         return
    
#     print("🔊 Generating voiceover...")
#     text = " ".join(text.split()[:300])
#     tts = gTTS(text, lang="en")
#     tts.save(output_file)
#     print("✅ Voiceover saved as", output_file)
