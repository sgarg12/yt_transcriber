
# Youtube Transcriber

I like trying out recipes on Youtube but not all creators have a text recipe to go along with the video.\
Playing and pausing the video while cooking is an annoyance.\
So I created this project which generates the transciption of any youtube video from its URL.

The speech recognition is done using [OpenAI's Whisper model](https://huggingface.co/openai/whisper-medium).


## Installation

A redis server is required to run the project, for example through docker:

```bash
  docker run -d --name worker-redis -p 6379:6379 redis
```
ffmpeg is also required and can be installed using:
```bash
  sudo apt install ffmpeg
```
Install the required packages using:
```bash
  pip install -r requirements.txt
```
Generate a `.env` file (see the `.env-example` provided).

Edit the `sender_email` variable in `email_sender.py`.


## Run Locally

1. Go to the project directory `cd yt_transcriber`
2. Start the Redis server
3. Start the worker using `dramatiq -p 1 -t 1 worker`. This creates 1 process and 1 worker thread for the process. This can be scaled depending on the requirements and machine being used.
4. Start the server using `uvicorn api:app`


## Usage/Examples
To generate a transcription make a `POST` request to `/generate-file` with the desired Youtube url. An optional email address can also be provided to send a link for the generated text file once the job is finished by the worker.

Any command line utility such as `HTTPie`can be used to make the requests. For example: 
```bash
http POST http://localhost:8000/generate-file url="https://www.youtube.com/anyID" email="any.email@gmail.com"
```
Response:
```bash
HTTP/1.1 201 Created
content-length: 149
content-type: application/json
date: Fri, 06 Oct 2023 02:43:58 GMT
server: uvicorn

{
    "completed": false,
    "created_at": "2023-10-05T22:43:59.141345",
    "file_name": null,
    "id": 1,
    "title": null,
    "url": "https://www.youtube.com/anyID"
}
```
The `file_name` field respresents the name of the uploaded resource to the bucket and `title` is the actual title of the youtube video. Both of these are automatically set once the generation is complete which can be determined using the `completed` field.



To check the status of a transcription, make a `GET` request to `/generated-file/{id}`. This can be useful if the email field isn't used when sending the `POST` request to obtain the status. For example: 
```bash
http GET http://localhost:8000/generated-file/1
```
Response:
```bash
HTTP/1.1 200 OK
content-length: 213
content-type: application/json
date: Thu, 05 Oct 2023 03:59:11 GMT
server: uvicorn

{
    "completed": true,
    "created_at": "2023-10-04T23:56:26.903960",
    "file_name": "a_file_name.txt",
    "id": 1,
    "title": "A Youtube Video",
    "url": "https://www.youtube.com/anyID"
}
```
To manually obtain a URL to download the generated text file (as opposed to providing an email) make a `GET` request to `/generated-file/{id}/url`. For example:
```bash
http GET http://localhost:8000/generated-file/1/url
```
Response:
```bash
HTTP/1.1 200 OK
content-length: 353
content-type: application/json
date: Fri, 06 Oct 2023 03:57:01 GMT
server: uvicorn

{
    "url": "https://some-storage-endpoint/storage-bucket-name/a_file_name.txt?some-signed-authorization-tokens&expiry-info"
}
```