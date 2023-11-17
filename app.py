# app.py
import time
from flask import Flask, Response, jsonify, render_template, request, redirect, url_for, session, flash
from openai import BadRequestError, OpenAI
import os
# from dotenv import load_dotenv
# load_dotenv()

app = Flask(__name__)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

@app.route('/')
def hello_world():

    start_time_prompt = time.time()
    description_completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Create a small description of a couple of words to create an image for Dall-E 3' "}]
    )
    description = description_completion.choices[0].message.content

    end_time_prompt = time.time()

    elapsed_time_prompt = end_time_prompt - start_time_prompt
    print('Elapsed time for prompt:', elapsed_time_prompt)

    start_time_image = time.time()
    immage_response = client.images.generate(
        model="dall-e-3",
        prompt=description,
        size="1024x1024",
        quality="standard",
        n=1,
        timeout=30
    )
    end_time_image = time.time()
    elapsed_time_image = end_time_image - start_time_image

    print('Elapsed time for image:', elapsed_time_image)

    dall_e_image_url = immage_response.data[0].url
    print(dall_e_image_url)

    dall_e_image_description = description_completion.choices[0].message.content
    print("Description of the DALL-E image:", dall_e_image_description)

    return render_template('index.html', generated_image_url=dall_e_image_url, generated_image_description=dall_e_image_description)
    


@app.route('/generate', methods=['POST'])
def generate():
    try: 
        imagePrompt = request.form['imagePrompt']
        print('Prompt:', imagePrompt)

        start_time = time.time()
        print('Start time:', start_time)
        imageResponse = client.images.generate(
            model="dall-e-3",
            prompt=imagePrompt,
            size="1024x1024",
            quality="standard",
            n=1,
            timeout=30
        )

        end_time = time.time()
        elapsed_time = end_time - start_time
        print('Elapsed time:', elapsed_time)

        # check response is ok
        print('Response is ok')
        image = imageResponse.data[0].url
        return jsonify({ 'image': image, 'prompt': imagePrompt })
    
    except BadRequestError as e:
        error_message = str(e)
        print('Internal Server Error:', error_message)
        return jsonify({'error': 'Bad Request', 'message': 'Your request was rejected as a result of our safety system. Your prompt may contain text that is not allowed by our safety system.'}), 400  # HTTP status code 400 for Bad Request
    
    except Exception as e:
        # Handle other exceptions
        error_message = str(e)
        print('Internal Server Error:', error_message)
        return jsonify({'error': 'Internal Server Error', 'message': error_message}), 500  # HTTP status code 500 for Internal Server Error



if __name__ == '__main__':
    app.run(debug=True)
    app.config["TEMPLATES_AUTO_RELOAD"] = True

