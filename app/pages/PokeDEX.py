import streamlit as st 
import requests
import copy 
import boto3
import json
import os 

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')

bedrock=boto3.client(service_name="bedrock-runtime", region_name= "us-east-1", 
                     aws_access_key_id=AWS_ACCESS_KEY_ID,
                     aws_secret_access_key=AWS_SECRET_KEY)

modelId = 'meta.llama2-70b-chat-v1'
accept = 'application/json'
contentType = 'application/json'
HF_AUTH = os.getenv('HF_AUTH')

API_URL_CLASS = "https://api-inference.huggingface.co/models/pniedziela96/vit-base-beans"
API_URL = "https://api-inference.huggingface.co/models/pniedziela96/blip-image-captioning-base-pokemon-finetune"
headers = {"Authorization": HF_AUTH}

def query(data):
    response = requests.post(API_URL_CLASS, headers=headers, data=data)
    return response.json()

def query_2(data):
    response = requests.post(API_URL, headers=headers, data=data)
    return response.json()

st.set_page_config(page_title="PokeDEX")

with st.sidebar:
    st.write("With PokeDEX you will no longer struggle with any type of Pokemon! :blue[Try it out!]")

st.header(" :blue[PokeDEX - check] :red[your Pokemon!] :frame_with_picture:")
st.write('Select the pokemon you want to check! The :red[PokeDEX] will describe what it can see and return all information available about recognized type!')
img = None 
desc = None 
lab = None
from PIL import Image
img = st.file_uploader("Upload your image here:", type=["jpg","png"], accept_multiple_files=False)
img2 = copy.deepcopy(img)


if img:
    output = query(img2)
    output_txt = query_2(img)
    try:
        image = Image.open(img)
    except Exception as e:
        img = None
        img2 = None
        st.write('Uploaded file failed, please investigate it or try another one.')

    
if img:     
    try: 
        desc = output_txt[0]['generated_text']
        lab = output[0]['label']
        st.image(image)
        st.write(f'**What can I see?**  {desc}')
        st.markdown(f'It has to be.. **:red[{lab}]!**')
        
        
        body = json.dumps({
        "prompt": f"\n\nHuman:Tell me all about {lab} you know. Pretend to be an expert from Pokemon world. Don't keep conversation.\n\nAssistant:",
        "max_gen_len":1500,
        "top_p":0.9,
        "temperature":0.1
        })
        
        response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
        response_body = json.loads(response.get('body').read())
        
        st.write(response_body.get('generation'))
    except Exception as e:
        st.write('Model is still loading... Please try again in 10-20 sec :sunflower:')
        st.markdown("<sub style='text-align: left; color: gray;'>Yep, that right! I'm trying to keep it running as cheap as possible hence this loading time :beer:</h5>", unsafe_allow_html=True)

st.divider()

st.header("How it works?")
st.write('The PokeDEX is consisted of three separate modules, namely: Image-Text Captioning, Type Classificator and RAG LLM.')
st.write('1. :blue[Image Captioning] : that\'s the first line that you can see under the upladed image. The BLIP model was finetuned on 833 Image-Text pairs of pokemons (I guess there are more Pokemons than that, but I\'m not a Pokemon trainer tho :smirk:) and deployend on HuggingFace Inference Endpoints (that\'s really cheap option for this case scenario).')
st.write('2. :blue[Classification] : Stright after the image description the classification comes into play (you can see it in this ":red[It has to be.. ]" line). For this task I selected very simple vit-b-16 and trained on 6991 labeled pokemon images.')
st.write('3. :blue[LLAMA2] : At this stage the designed prompt (to pretend a Pokemon expert) is used to query the LLAMA2 FM using classified Pokemon type.')

st.write('Would it be possible to make this better? :green[Certainly YES]. But it was not my purpose here.')

