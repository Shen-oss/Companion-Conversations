from revChatGPT.V3 import Chatbot as V3
from listen import listen
from TTS.Vits import TextToSpeak
from PERT.EmotionClassification import EmotionClassification

import speech_recognition as sr
import logging
import socket
import geocoder
import requests
import cv2
import base64
import unicodedata

engine = ["gpt-4-vision-preview", 
          "gpt-3.5-turbo"
          ]

character_list = ['派蒙', '鐘離', '胡桃']

key_word = {"開心" : "0", "超級生氣" : "1", "難過" : "2", "疑惑" : "3", "害羞":"4", "驚訝" : "5", "微生氣" : "6", "無情緒" : "7", "視覺" : "8"}

image_path = "<you image path>"

udp_ip = "127.0.0.1"  # Unity运行在同一台计算机上时，可以使用本地回环地址
udp_port = 34567  # 与Unity接收端使用相同的端口

# 创建Socket对象
server_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket1.bind((udp_ip, 12345))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 设置发送缓冲区大小
sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)

logging.basicConfig(filename='conversation.log', level=logging.DEBUG, format='%(asctime)s - %(message)s', encoding='utf-8')

emotionClassification = EmotionClassification('PERT/EmotionClassification_150.pt')

tts = TextToSpeak(filename="<Unity project assets path>")

def characterSetUp(character_name):
    
    character_dict = {'派蒙' : 'paimeng', '鐘離' : 'Scumbag', '胡桃' : 'Bitch'}
    role = ""

    try:
        with open(f'role/{character_dict.get(character_name)}.txt', 'r', encoding='utf8') as f:
            role = f.read()

        chatbot = V3(
            api_key = "<api key>",
            system_prompt = role,
            engine = engine[1],
            temperature = 0.0,
            presence_penalty = 0.0,
            frequency_penalty= 0.0
            )

        chatbot.reset()

        return chatbot
    
    except:
        print("角色不存在")

        chatbot = V3(
                api_key = "<api key>",
                system_prompt = role,
                engine = engine[1],
                temperature = 1.0,
                presence_penalty = 1.0,
                frequency_penalty= 1.0
                )
            
        chatbot.reset()

        return chatbot
     


    
def get_img():
    # 打开摄像头
    cap = cv2.VideoCapture(0)  # 0 表示默认摄像头，如果有多个摄像头，可以尝试不同的编号

    # 捕获一帧图像
    ret, frame = cap.read()

    # 保存捕获的图像到文件
    cv2.imwrite("img/result.jpg", frame)

    # 释放摄像头资源
    cap.release()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def get_current_location():
    # 使用Geocoder库获取IP地址
    ip_info = geocoder.ip('me')

    # 获取IP地址
    ip_address = ip_info.ip

    # 使用IP地址查询位置信息
    response = requests.get(f"https://ipinfo.io/{ip_address}/json")

    if response.status_code == 200:
        data = response.json()
        city = data.get("city", "未知城市")
        region = data.get("region", "未知地区")
        country = data.get("country", "未知国家")
        loc = data.get("loc", "未知坐标")

        latitude, longitude = loc.split(',')
        print("当前设备位置：")
        print("IP地址:", ip_address)    
        print("城市:", city)
        print("地区:", region)
        print("国家:", country)
        print("纬度:", latitude)
        print("经度:", longitude)
        return city, region
    else:
        print("无法获取位置信息")

def fullwidth_to_halfwidth(text):
    # 使用unicodedata.normalize將全形字符轉換為NFKC形式
    normalized_text = unicodedata.normalize('NFKC', text)
    
    # 將轉換後的文本中的全形字符替換為半形字符
    return ''.join([c if unicodedata.category(c) not in ['Mn', 'Mc'] else '' for c in normalized_text])

def ask_stream(prompt, chatbot):

    completeText = ""
    base64_image = None
    if(("看起來" in prompt or "這張圖" in prompt) and chatbot.engine =="gpt-4-vision-preview"):
        get_img()
        # Path to your image
        
        # Getting the base64 string
        base64_image = encode_image(image_path)

    for message in chatbot.ask_stream(prompt, img=base64_image):

        if ("。" in message or "！" in message or "？" in message or "\n" in message):
            completeText += message
            if(len(completeText) > 2):
                emotionSatae = ""
                emotionSatae = str(emotionClassification.infer(completeText))
                print(f"{character_list[character]}: ") 
                print(completeText, end="", flush=True)
                print(emotionSatae)
                if character_list[character] == "派蒙":
                    tts.TTS("Paimon", completeText) 
                else:
                    completeText = fullwidth_to_halfwidth(completeText)
                    completeText = completeText.replace("\n", "")
                    tts.fastTTS('Zhongli'if character_list[character] == "鐘離" else 'Hutao', completeText)
                state = listen(server_socket1, 12345)
                
                logging.info(u"chatbot:{}".format(completeText))

                sock.sendto((character_list[character] + "&" + completeText + "&" + emotionSatae).encode(), (udp_ip, udp_port))
                completeText = ""

        else:
            completeText += message

def ask_stream_customer(prompt):

    completeText = ""
    
    for message in prompt:

        if ("。" in message or "！" in message or "？" in message or "\n" in message):
            completeText += message
            if(len(completeText) > 2):
                emotionSatae = ""
                emotionSatae = str(emotionClassification.infer(completeText))
                print(f"{character_list[character]}: ") 
                print(completeText, end="", flush=True)
                print(emotionSatae)
                if character_list[character] == "派蒙":
                    tts.TTS("Paimon", completeText)
                else:
                    completeText = fullwidth_to_halfwidth(completeText)
                    completeText = completeText.replace("\n", "")
                    tts.fastTTS('Zhongli'if character_list[character] == "鐘離" else 'Hutao', completeText)
                state = listen(server_socket1, 12345)
                
                logging.info(u"chatbot:{}".format(completeText))

                sock.sendto((character_list[character] + "&" + completeText + "&" + emotionSatae).encode(), (udp_ip, udp_port))
                completeText = ""

        else:
            completeText += message


def voice_to_text():

    # 創建語音辨識器物件
    r = sr.Recognizer()
    r.pause_threshold = 0.5
    # 開啟麥克風並進行錄音
    with sr.Microphone() as source:
        print("\n請開始說話...")
        sock.sendto(("請開始說話").encode(), (udp_ip, udp_port))
        r.adjust_for_ambient_noise(source, duration=0.5) # 噪音抑制，自動調整麥克風靜音閾值
        audio = r.listen(source) # 設置錄音時間上限為 10 秒

    # 使用Google語音辨識引擎將錄音轉換為文字
    try:
        text = r.recognize_google(audio, language="zh")
        # text = converter.convert(text)
        # to_txt(text, "user")
        sock.sendto(("我&" + text).encode(), (udp_ip, udp_port))
        logging.info(u"使用者:{}".format(text))
        print("我:" + text)
        
        return text
    except sr.UnknownValueError:
        # 如果無法辨識語音，返回錯誤提示
        # print("無法辨識您的語音")
        sock.sendto(("我&@!#!@#!@#!@#@!").encode(), (udp_ip, udp_port))
        logging.info(u"使用者:@!#!@#!@#!@#@!")
        return "請表示自己聽不清楚"
    except sr.RequestError as e:
        # 如果無法連線至Google語音辨識服務，返回錯誤提示
        # print("無法連線至Google語音辨識服務：{0}".format(e))
        return "錯誤"


def main():

    global character
    character = 0
    
    chatbot = characterSetUp(character_list[character])
    
    city, region = get_current_location()
    state = ""
    Imeg = "好啦，聽好了！我們從原神遊戲裡帶來了我，派蒙，還有我的個性呢！現在你聽到的聲音，都是用語音克隆技術生成的，是不是很酷？而且呀，你只要在提問時用對關鍵字，我就能「看見」你啦！我們的目標是讓大家都能隨心所欲地表達自己的情感，找到一個宣泄的小天地。無論是心理有困擾的朋友，還是社交上有點手足無措的人，都很適合跟我聊天哦！"
    ask_stream_customer(Imeg)
    sock.sendto("recode".encode(), (udp_ip, 34569))

    while True:

        state = listen(server_socket1,12345)
        if state != 'switch':
            state = False
            prompt = voice_to_text()    
            ask_stream(prompt, chatbot)

            sock.sendto("recode".encode(), (udp_ip, 34569))
        else:
            if character <len(character_list) - 1:
                character += 1
            else:
                character = 0

            chatbot = characterSetUp(character_list[character])
if __name__ == '__main__':
    main()