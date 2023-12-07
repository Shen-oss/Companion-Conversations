# from main import tts
from TTS.Vits import TextToSpeak
from revChatGPT.V3 import Chatbot
from listen import listen
import socket
import unicodedata

udp_ip = "127.0.0.1"  # Unity运行在同一台计算机上时，可以使用本地回环地址
udp_port = 34567  # 与Unity接收端使用相同的端口


# 创建Socket对象
server_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket1.bind((udp_ip, 12345))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tts = TextToSpeak(filename="<Unity project assets path>")

def fullwidth_to_halfwidth(text):
    # 使用unicodedata.normalize將全形字符轉換為NFKC形式
    normalized_text = unicodedata.normalize('NFKC', text)
    
    # 將轉換後的文本中的全形字符替換為半形字符
    return ''.join([c if unicodedata.category(c) not in ['Mn', 'Mc'] else '' for c in normalized_text])

def ask_stream(prompt, role, chatbot):

    totalText = ""
    completeText = ""
    base64_image = None
    
    for message in chatbot.ask_stream(prompt, img=base64_image):
        
        if ("。" in message or "！" in message or "？" in message or "\n" in message or "；" in message):

            completeText += message
            
            if(len(completeText) > 2):
                print(role + "：" + completeText) 
                # print(completeText)
                completeText = fullwidth_to_halfwidth(completeText)
                completeText = completeText.replace("\n", "")
                if "鍾離" in role:
                    tts.fastTTS('Zhongli', completeText, 1)
                    state = listen(server_socket1, 12345)
                    sock.sendto(("鍾離&" + completeText).encode(), (udp_ip, udp_port))
                    
                elif "派蒙" in role:
                    tts.TTS("Paimon", completeText)   
                    state = listen(server_socket1, 12345)
                    sock.sendto(("派蒙&" + completeText).encode(), (udp_ip, udp_port))  
                else:
                    tts.fastTTS('Hutao', completeText, 1)
                    state = listen(server_socket1, 12345)
                    sock.sendto(("胡桃&" + completeText).encode(), (udp_ip, udp_port))
                completeText = ""

        else:
            completeText += message
        totalText += message 
    return totalText

with open('role/role.txt', 'r', encoding='utf8') as f:
    role_paimon = f.read()

with open('role/Scumbag.txt', 'r', encoding='utf8') as f:
    role_Zhongli = f.read()

with open('role/Bitch.txt', 'r', encoding='utf8') as f:
    role_Hutao = f.read()

engine = ["gpt-4-vision-preview", 
          "gpt-3.5-turbo-16k",
          "gpt-3.5-turbo"
          ]

# # OpenAI API Key
api_key = "<api key>"

chatbot = Chatbot(api_key= api_key,
                  system_prompt= role_paimon,
                  engine=engine[1],
                  temperature = 1.0,
                  presence_penalty = 0.6,
                  frequency_penalty= 0.6)

chatbot2 = Chatbot(api_key= api_key,
                  system_prompt = role_Zhongli,
                  engine=engine[2],
                  temperature = 0.9,
                  presence_penalty = 1.0,
                  frequency_penalty= 1.0)

chatbot3 = Chatbot(api_key= api_key,
                  system_prompt = role_Hutao,
                  engine=engine[2],
                  temperature = 0.7,
                  presence_penalty = 1.0,
                  frequency_penalty= 1.0)

# paimon_response = ask_stream("跟我打招呼並自我介紹", "派蒙", chatbot)
meg = "第一回你先露一點小破綻給我"
zhongli_response = ask_stream(meg, "鍾離", chatbot2)
# chatbot3.add_to_conversation(meg, 'assistant')
# hutao_response = ask_stream("跟我打招呼並自我介紹", "胡桃", chatbot3)
while True:
    hutao_response = ask_stream(zhongli_response, "胡桃", chatbot3)
    zhongli_response = ask_stream(hutao_response, "鍾離", chatbot2)
    # paimon_response = ask_stream(zhongli_response, "派蒙", chatbot)
    
# zhongli_response = ask_stream(paimon_response, "Zhongli", chatbot2)
# paimon_response = ask_stream(zhongli_response, "paimon", chatbot)
