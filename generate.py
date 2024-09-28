import json
import openai
openai.api_base = "https://yeysai.com/v1"
openai.api_key="sk-TmqNTUwMzp2RXHmG3d44868eD27247E4A0771bA203D8922d"
def chatgpt(messages):
        try:
            response = openai.ChatCompletion.create(
          #  model='gpt-3.5-turbo-1106',
            model='gpt-4-1106-preview',
            messages=messages,
            temperature=0.1,
            )
            answer = response.choices[0].message["content"]
            return answer
        except Exception as exc:
            error_message = f"Error: {str(exc)}"
            return error_message

with open('original_table.json','r',encoding='utf-8') as g :
    directory=json.load(g)

with open('diabetes_content.json', 'r', encoding='utf-8') as file:
    articles = [json.loads(line) for line in file]


def search_and_update(json_obj, outlines,target_key, new_value):
    """
    递归地搜索嵌套的 JSON 对象中的指定键，并更新其值。

    参数:
    - json_obj: 要搜索的 JSON 对象（字典或列表）
    - target_key: 要搜索的键
    - new_value: 要插入的新值
    """
    if isinstance(json_obj, dict):
        for key in json_obj:
            if key == target_key:
                value_obj=json_obj[key]
                if(isinstance(value_obj, str)):
                    old_value=json_obj[key]
                    json_obj[key] =old_value+new_value
                if(isinstance(value_obj, dict)):
                    get_title_prompt=f"""You will receive a summary of a text. Please draft a general subtitles based on the summary.The format of the title can be referred to {outlines}.\nOutput format: subtitle . Only one line of content will be output. \nSummary: {new_value}\nPlease give your subtitle without any extra words.Make sure the title is general"""
                    messages=[{"role":"user","content":get_title_prompt}]
                    title=chat_gpt(messages)
                    obj=json_obj[key]
                    obj[title]=new_value

            else:
                search_and_update(json_obj[key],outlines, target_key, new_value)
    elif isinstance(json_obj, list):
        for item in json_obj:
            search_and_update(item,outlines, target_key, new_value)


def split(obj,max_length):
    titles=list(obj.keys())
    for key,value in dict.items():
        if isinstance(value, dict):
            split(obj[key],max_length)
        if isinstance(value, str):
            if(len(value)>max_length):
                if(key=="others"):
                    
                else:
                    obj[key]=split_new(value,key)

def split_new(value,original_title):
    split_prompt="You will receive a lot of texts related to {original_title}. Each text begins with a number in brackets as its serial number. Your task is to classify these texts and come up with a separate title for each class. Please output a title and the serial number of the corresponding texts on each line. The title and serial number are separated by '//', and multiple serial numbers are separated by ','. \nSample output: Output value growth //2,3,5\nGreen agriculture //0,1\nNote: 1. The titles should be short and there is no need to repeat fields related to common topics such as {original_title}; 2. The output must comply with the format requirements and wrap after the serial number set of each title; 3. You can divide the texts into NO MORE THAN 4 classes. \nBelow are multiple texts: \n{value}\nPlease answer the classification results directly in the required format without any extra words."


def merge(obj,max_num):
    )

def search(obj,text,num,depth=0):
    titles=list(obj.keys())
    if isinstance(obj, dict):
        if(depth=0):
            select_title_prompt=f"""You will receive a section heading library and a text for diabetes trials. Please follow the steps below: 1. Understand the text and find the heading that match the text from the section heading library, with no more than 2 best match headings. 2. Summarize the content from the text that is related to each heading. 3. Each line of output must contain two parts: 'subsection heading&&Summary content'. 4. If there is no any heading that matches the text, output 'None'. \n Sample output: Symptoms of COVID-19&&A small number of patients with COVID-19 may experience severe headaches. \n Oral medication&&The trial found that the combination of Nirmatrelvir and Ritonavir 2 was significantly better than using them separately in relieving symptoms such as breathing difficulties and severe headaches caused by COVID-19. \nNote: 1. Output must be in the required format, and only wrap after the summary content; 2. Select headings that are most related to the text, otherwise output 'None' when there is no any related heading; 3. Do not select more than 2 headings. \nHeading library: {titles}\nText: {text}\n\nPlease answer the matched headings directly, one per line, without extra words.""" 
        else:
            select_title_prompt=f"""You will receive a section heading library and a text for diabetes trials. Please follow the steps below: 1. Understand the text and find the heading that match the text from the section heading library. 2. Summarize the content from the text that is related to the heading. 3. The output must contain two parts: 'subsection heading&&Summary content'. 4. If there is no any heading that matches the text, output 'None'. \n Sample output: \n Oral medication&&The trial found that the combination of Nirmatrelvir and Ritonavir 2 was significantly better than using them separately in relieving symptoms such as breathing difficulties and severe headaches caused by COVID-19. \nNote: 1. Output must be in the required format; 2. Select headings that are most related to the text, otherwise output 'None' when there is no any related heading; \nHeading library: {titles}\nText: {text}\n\nPlease answer the matched headings directly without extra words."""
        messages=[{"role":"user","content":select_title_prompt}]
        title=chatgpt(messages)
       # title="None"
        ##生成新的标题
        if(title=="None"or "None" in title):
            summary_prompt="Please generate a summary based on the text provided. \nText: {text}\n\nPlease directly respond with your summary without any redundant words."
            messages=[{"role":"user","content":summary_prompt}]
            summary=chatgpt(messages)
            summary="["+num+"]"+summary+"\n"
            if("others" in titles):
                obj["others"]+=summary
            else:
                obj["others"]=summary
        else:
            title=title.replace("\n\n","\n").split("\n")
            for i in range(len(title)):
                line=title[i].split("&&")
                name=line[0]
                summary="["+num+"]"+line[1]+"\n"
                obj_=obj[name]
                if isinstance(obj_, dict):
                    search(obj[name],text,num,depth+1)
                if isinstance(obj_, str):
                    obj[name]+=summary

                


def generate_wiki(directory, articles):
    for i in range(0,401):
        article=articles[i]
        text=article["content"]
        num=article["id"]
        try:
            seach(directory,text,num)
        except Exception as exc:
            error_message = f"Error: {str(exc)}"
            print(error_message)
            continue
        if(article["id"]%10==0):
            name=f"""output6/step_{article["id"]}.json"""
            with open(name, 'w') as file:
                json.dump(directory, file, indent=4)

            split(directory,3000)
            name1=f"""output6/split_{article["id"]}.json"""
            with open(name1, 'w') as file:
                json.dump(directory, file, indent=4)

            directory=merge(directory,4)
            name2=f"""output6/merge_{article["id"]}.json"""
            with open(name2, 'w') as file:
                json.dump(directory, file, indent=4)

generate_wiki(directory, articles)
