import time
import streamlit as st
import random
import json
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_type = os.getenv("OPENAI_API_TYPE")
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_version = os.getenv("OPENAI_API_VERSION")
openai.api_key = os.getenv("OPENAI_API_KEY")

gua_dict = {
    '阳阳阳': '乾',
    '阴阴阴': '坤',
    '阴阳阳': '兑',
    '阳阴阳': '震',
    '阳阳阴': '巽',
    '阴阳阴': '坎',
    '阳阴阴': '艮',
    '阴阴阳': '离'
}

number_dict = {
    0: '初爻',
    1: '二爻',
    2: '三爻',
    3: '四爻',
    4: '五爻',
    5: '六爻',
}

with open('gua.json') as gua_file:
  file_contents = gua_file.read()
des_dict = json.loads(file_contents)


st.set_page_config(
    page_title="六爻游戏",
    page_icon="🔮",
    layout="centered",
)

st.markdown('## 六爻游戏')
st.markdown(""" 
> 本网站**仅供娱乐**，并非用来算命、迷信或卜卦的工具。所有的结果都是随机生成的，我们强烈建议用户不要受其内容的影响来做出任何决策。  
> 此外，其生成结果的过程仅供参考，只是游戏流程的一部分，不代表任何正统操作。  
> 这个网站只是为了测试和娱乐，不允许用于商业用途，所有的内容都不能当作真实的，未成年人请勿使用。请各位用户理性对待，保持娱乐的心态，不要依赖或深信其结果。  
             
[网站源代码](https://github.com/RealKai42/liu-yao-divining)    
🥺 玩的开心记得点个 star 呀～
""")
st.markdown("""
            六爻为丢 **六次** 三枚硬币，根据三枚硬币的正反（字背）对应本次阴阳，三次阴阳对应八卦中的一卦  
            六次阴阳对应六爻，六爻组合成两个八卦，对应八八六十四卦中的卦辞，根据卦辞进行 **随机** 解读  
              
            为保证可用性和成本限制，每次只能提问**一个问题**，请谨慎提问
            """)

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": [{"type": "text", "content": "告诉我你心中的疑问吧 ❤️"}]
    }]
if "disable_input" not in st.session_state:
    st.session_state.disable_input = False

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        for content in message["content"]:
            if content["type"] == "text":
                st.markdown(content["content"])
            elif content["type"] == "image":
                st.image(content["content"])
            elif content["type"] == "video":
                st.video(content["content"])


def add_message(role, content):
     with st.chat_message(role):
        message_placeholder = st.empty()
        full_response = ""

        for chunk in content.split():
            full_response += chunk + " "
            time.sleep(0.1)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)


def get_3_coin():
    return [random.randint(0, 1) for _ in range(3)]

def get_yin_yang_for_coin_res(coin_result):
    return "阳" if sum(coin_result) > 1.5 else "阴"

def get_number_for_coin_res(coin_result):
    return 1 if sum(coin_result) > 1.5 else 0

def format_coin_result(coin_result, i):
    return f"{number_dict[i]} 为 " + "".join([f"{'背' if i>0.5 else '字'}" for i in coin_result]) + " 为 " + get_yin_yang_for_coin_res(coin_result)

def disable():
    st.session_state["disable_input"] = True

if question := st.chat_input(placeholder="输入你内心的疑问", key='input', disabled=st.session_state.disable_input, on_submit=disable):
    add_message("user", question)
    first_yin_yang = []
    for i in range(3):
        coin_res = get_3_coin()
        first_yin_yang.append(get_yin_yang_for_coin_res(coin_res))
        add_message("assistant", format_coin_result(coin_res, i))

    first_gua = gua_dict["".join(first_yin_yang)]
    add_message("assistant", f"您的首卦为：{first_gua}")

    second_yin_yang = []
    for i in range(3, 6):
        coin_res = get_3_coin()
        second_yin_yang.append(get_yin_yang_for_coin_res(coin_res))
        add_message("assistant", format_coin_result(coin_res, i))
    second_gua = gua_dict["".join(second_yin_yang)]
    add_message("assistant", f"您的次卦为：{second_gua}")

    gua = first_gua + second_gua  
    gua_des = des_dict[gua]
    with st.chat_message("assistant"):
        st.markdown(f"""
        六爻结果: {gua}  
        卦名为：{gua_des['name']}   
        {gua_des['des']}   
        卦辞为：{gua_des['sentence']}   
    """)
        
    response = openai.ChatCompletion.create(
        engine="gpt35",
        messages = [{"role":"system","content":"你是出生于一个中华六爻世家的算卦人，你可以根据来者所占卜之事和卦象，并利用这个卦象解释为来者所占卜之事提供有效的建议，并尽可能乐观积极向上的回答，引导占卜之人向好的方向发展。"},
                    {"role":"user","content":f"""
                    问题是：{question},
                    六爻结果是：{gua},
                    卦名为：{gua_des['name']},
                    {gua_des['des']},
                    卦辞为：{gua_des['sentence']}"""},
                    ],
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
    with st.chat_message("assistant"):
        st.markdown(response.choices[0].message.content)
