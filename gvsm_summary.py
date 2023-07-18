import openai
import streamlit as st
import requests
import os
import json
from datetime import datetime
import hmac, hashlib
from pytz import timezone

def gpt_summarize(text):
    # system_instruction = "assistant는 user의 입력을 bullet point로 3줄 요약해준다."
    system_instruction = "assistant는 user의 입력을 26자로 요약해준다."

    messages = [{"role": "system", "content": system_instruction},
                {"role": "user", "content": text} 
                ]

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    result = response['choices'][0]['message']['content']
    return result

# timestamp 생성
timestamp = datetime.now(timezone("Asia/Seoul")).strftime("%Y%m%d%H%M%S%f")[:-3] 

# client_id = "TEST_CLIENT_ID";
# client_secret = "8c1b1f08f68414d84ce31a66c2edcc2b43a72407fccc7699fd47c4ffd1b20896";
client_id = "glabs_95af7c3cf7b6f11f74f3d47774c1d3eeeea39e6dd65f25fade9d09ff3abc8047";
client_secret = "dc9691b9e161032808b028252de11382afee09e5594a16efc7e887fced7099a9";
client_key = "e8f79e24-8fe3-5c0f-9a75-8a9b823a1261"

# HMAC 기반 signature 생성
signature = hmac.new(
      key=client_secret.encode("UTF-8"), msg= f"{client_id}:{timestamp}".encode("UTF-8"), digestmod=hashlib.sha256
  ).hexdigest()

url = "https://aiapi.genielabs.ai/kt/nlp/summarize-news"
headers = {
     "x-client-key":f"{client_key}",
     "x-client-signature":f"{signature}",
     "x-auth-timestamp": f"{timestamp}",
     "Content-Type": "application/json",
     "charset": "utf-8",
}  

def genie_summarize(text):
    body = json.dumps({"text" : f"{text}", "beam_size" : 3})
    # Genie 뉴스요약 API 요청
    response = requests.post(url, data=body, headers=headers, verify=False)
    
    if response.status_code == 200:
       try:
           data = response.json()
           summary = data['result']['summary']
       except json.decoder.JSONDecodeError:
           summary = print(f'json.decoder.JSONDecodeError occured.\nresponse.text: "{response.text}"')
    else:
         summary = print(f"response.status_code: {response.status_code}\nresponse.text: {response.text}")
    
    return summary

st.title("ChatGPT와 Midm 뉴스요약 비교")

input_text = st.text_area("여기에 뉴스기사를 입력해주세요", height=300)
openai.api_key = st.text_input('Your OpenAI API Key', type = 'password', disabled=not input_text)

if st.button("뉴스요약 비교"):
    if input_text:
        try:
            gpt_summary = gpt_summarize(input_text)
            st.write(':sunglasses: ChatGPT 뉴스요약(gpt-3.5-turbo)')
            st.success(gpt_summary)
            
            genie_summary = genie_summarize(input_text)
            st.write(':sunglasses: Midm 뉴스요약(Midm-3B)')
            st.success(genie_summary)
        except:
            st.error("요청 오류가 발생했습니다")
    else:
        st.warning("텍스트를 입력하세요")
