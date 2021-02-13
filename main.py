import os
import sys
import tempfile
from shutil import rmtree

from flask import Flask, request, send_file
import youtube_dl


for_clean_dirs_file = 'for_clean_dirs.txt'

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'verbose': True,
}

app = Flask(__name__)


def perform_cleaning():
    if os.path.isfile(for_clean_dirs_file):
        with open(for_clean_dirs_file, 'r') as f:
            for dir_path in f:
                if os.path.isdir(dir_path):
                    rmtree(dir_path)
        os.remove(for_clean_dirs_file)


def add_for_cleaning(dir_path):
    with open(for_clean_dirs_file, 'a') as f:
        f.write(dir_path + '\n')


def get_video_url(url, args):
    url += '?'
    for k in args:
        url += f'{k}={args[k]}&'
    return url[:-1]


def get_file_name():
    return max(os.listdir('.'), key=os.path.getctime)


@app.route('/download/<path:url>')
def download(url):
    url = get_video_url(url, request.args)

    current_opts = ydl_opts.copy()

    tmp_dir_name = tempfile.mkdtemp()
    current_opts['outtmpl'] = f'{tmp_dir_name}/%(title)s.mp3'

    with youtube_dl.YoutubeDL(current_opts) as ydl:
        ydl.download([url])

    filename = tmp_dir_name + '/' + os.listdir(tmp_dir_name)[0]
    app.logger.info(f'Downloaded video: {filename}')

    add_for_cleaning(tmp_dir_name)

    return send_file(filename, as_attachment=True)


@app.route('/')
def default():
    return 'Enjoy'


if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 34341
    app.run(debug=True, host='0.0.0.0', port=port)