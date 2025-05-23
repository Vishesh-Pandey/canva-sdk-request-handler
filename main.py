from openai import OpenAI
from flask import Flask
from flask import request
from canva_rag import handle_rag
import openai
from pydantic import BaseModel

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

class StepBreakdown(BaseModel):
    steps: list[str]
    rag_query : list[str]

@app.route("/canvarequest" , methods=['POST'])
def canvarequest():

    user_input = request.get_json()['user_input']

    step_client = OpenAI()
    step_prompt = f'''
    #Break down the given input into smaller technical step commands seperated by comma to generate a document.
    - Example : 
    if given input is "Add information about animal on the page" then output should be :
    Add heading about animal on the page, Add image about animal at center of the page, Add paragraph about animal at bottom of the page
    Also according to command provide the list of rag query required for steps. Here is the list of rag query:
    - An element that renders image content.
    - An element that renders image content and has positional properties.
    - An element that renders video content.
    - An element that renders video content and has positional properties.
    - An element that renders text content.
    - An element that renders text content and has positional properties.
    - An element that renders rich text content.
    - An element that renders rich text content and has positional properties.
    - An element that renders rich media, such as a YouTube video.
    - An element that renders rich media, such as a YouTube video, and has positional properties.
    - An element that renders a vector shape.
    - An element that renders a vector shape and has positional properties.
    - An element that renders a table.
    - An element that renders a table and has positional properties.
    - An element that renders a vector shape.
    - An element that renders a vector shape and has positional properties.
    - An element that renders a table.
    - An element that renders a table and has positional properties.
    '''

    response = step_client.responses.parse(
        model="gpt-4.1",
        input=[
        {
            "role": "system",
            "content": step_prompt,
        },
        {"role": "user", "content": user_input},
    ],
        text_format=StepBreakdown,
    )

    print("Step Breakdown : " , response)
    print("STEP BREAKDOWN WITH OUTPUT PRASED : " , response.output_parsed)

    all_steps = response.output_parsed

    return_type_format = handle_rag(all_steps.rag_query)

    prompt = f'''
    Return array of json value in the following format according for given input steps :
    {return_type_format} 
    '''

    user_steps = ",".join(all_steps.steps)
    
    client = OpenAI()

    response = client.responses.create(
        model="gpt-4.1",
        instructions=prompt,
        input=user_steps,
    )

    return response.output_text


if __name__ == "__main__":
    app.run()


