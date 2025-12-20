from flask import Flask, request, send_file, jsonify
from pytubefix import YouTube
from flask_cors import CORS
import os
import uuid
import subprocess

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/get_streams", methods=["POST"])
def get_streams():
    url = request.json.get("url")
    yt = YouTube(url)

    video_streams = yt.streams.filter(progressive=False, file_extension="mp4", type="video")
    audio_streams = yt.streams.filter(only_audio=True, mime_type="audio/mp4")

    qualities = sorted({stream.resolution for stream in video_streams if stream.resolution}, reverse=True)

    return jsonify({
        "title": yt.title,
        "qualities": qualities
    })


@app.route("/download", methods=["POST"])
def download_video():
    data = request.json
    url = data.get("url")
    format_type = data.get("format")
    quality = data.get("quality")

    yt = YouTube(url)

    if format_type == "mp3":
        audio = yt.streams.filter(only_audio=True).first()
        filename = f"{uuid.uuid4()}.mp3"
        temp = audio.download(filename="temp.mp4")
        subprocess.run(["ffmpeg", "-i", temp, filename, "-y"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        os.remove(temp)
        return send_file(filename, as_attachment=True)

    else:  # mp4
        video_stream = yt.streams.filter(res=quality, mime_type="video/mp4").first()
        audio_stream = yt.streams.filter(only_audio=True, mime_type="audio/mp4").first()

        video_file = f"video_{uuid.uuid4()}.mp4"
        audio_file = f"audio_{uuid.uuid4()}.mp4"
        output_file = f"{yt.title.replace(' ', '_')}_{quality}.mp4"

        video_stream.download(filename=video_file)
        audio_stream.download(filename=audio_file)

        subprocess.run(["ffmpeg", "-i", video_file, "-i", audio_file, "-c", "copy", output_file, "-y"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        os.remove(video_file)
        os.remove(audio_file)

        return send_file(output_file, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
