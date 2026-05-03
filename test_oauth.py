from pytubefix import YouTube
import time

def v(url, code):
    print(f"VERIFIER_CALLED: {url} | {code}")

print("Starting YouTube init...")
try:
    yt = YouTube("https://www.youtube.com/watch?v=aqz-KE-bpKQ", 
                 use_oauth=True, 
                 oauth_verifier=v)
    print(f"Title: {yt.title}")
    print("YouTube init finished.")
except Exception as e:
    print(f"Error: {e}")
