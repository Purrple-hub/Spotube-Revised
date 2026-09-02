import os
import Spotube as ST
from flask import Flask, render_template, request
import logging

def create_app():
    app = Flask(__name__)

    @app.get('/')
    def index():
        return render_template('index.html')

    @app.post('/download')
    def download():
        spotify_url = request.form.get('spotify_url', '').strip()
        output_dir = request.form.get('output_dir', 'Spotube_Downloads').strip()
        if not ST.is_spotify_url(spotify_url):
            return render_template(
                'index.html',
                error='Enter a valid Spotify track, album, or playlist URL.',
            ), 400
        try:
            dataframe, manifest = ST.spotify_handling(spotify_url, output_dir)
        except Exception as exc:
            logging.exception('Download failed')
            return render_template('index.html', error=str(exc)), 500
        return render_template(
            'index.html',
            files=dataframe.to_dict(orient='records'),
            manifest=manifest,
        )

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Referrer-Policy'] = 'no-referrer'
        return response

    return app


app = create_app()


def start_server():
    app.run(
        host=os.getenv('SPOTUBE_HOST', '127.0.0.1'),
        port=int(os.getenv('SPOTUBE_PORT', '5000')),
        debug=False,
    )


def uh_oh():
    print('Server is running. Press Ctrl+C to stop.')
    start_server()