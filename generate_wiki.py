import json
import openai
from sentence_transformers import SentenceTransformer
import torch

openai.api_base = "https://yeysai.com/v1"
openai.api_key="sk-TmqNTUwMzp2RXHmG3d44868eD27247E4A0771bA203D8922d"
model = SentenceTransformer('gtr-base')


def chatgpt(messages):
        try:
            response = openai.ChatCompletion.create(
          #  model='gpt-3.5-turbo-1106',
            model='gpt-4o',
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




def split(obj,max_length):
    titles=list(obj.keys())
    for key,value in obj.items():
        if isinstance(value, dict):
            split(obj[key],max_length)
        if isinstance(value, str):
            if(len(value)>max_length):
                if(key=="others"):
                    split_prompt=f"""You will receive a lot of texts related to diabete. Each text begins with a number in brackets as its serial number. Your task is to classify these texts and come up with a separate title for each class. Please output a title and the serial number of the corresponding texts on each line. The title and serial number are separated by '//', and multiple serial numbers are separated by ','. \nSample output: Output value growth//2,3,5\nGreen agriculture//0,1\nNote: 1. The output must comply with the format requirements and wrap after the serial number set of each title; 2. You can divide the texts into NO MORE THAN 4 classes. \nBelow are multiple texts: \n{value}\nPlease answer the classification results directly in the required format without any extra words."""
                    messages=[{"role":"user","content":split_prompt}]
                    gpt_answer=chatgpt(messages)
                   # print(gpt_answer)
                    classes=gpt_answer.replace("\n\n","\n").split("\n")
                    if(len(classes)==1):
                        return 
                    articles=value.split("\n")
                    for new_class in classes:
                        parts=new_class.split("//")
                        new_title=parts[0]
                        numbers=parts[1].split(",")
                        new_content=""
                        for number in numbers:
                            prefix="["+number+"]"
                            for article in articles:
                                if article.startswith(prefix):
                                    new_content+=article
                                    new_content+="\n"
                        obj[new_title]=new_content
                    obj["others"]=""
                    break
                else:
                    split_prompt=f"""You will receive a lot of texts related to {key}. Each text begins with a number in brackets as its serial number. Your task is to classify these texts and come up with a separate title for each class. Please output a title and the serial number of the corresponding texts on each line. The title and serial number are separated by '//', and multiple serial numbers are separated by ','. \nSample output: Output value growth//2,3,5\nGreen agriculture//0,1\nNote: 1. The output must comply with the format requirements and wrap after the serial number set of each title; 2. You have to divide the text into more than 1 classes. 3. You can divide the texts into NO MORE THAN 4 classes. 4.Each text can only have one category.\nBelow are multiple texts: \n{value}\nPlease answer the classification results directly in the required format without any extra words."""
                    messages=[{"role":"user","content":split_prompt}]
                    gpt_answer=chatgpt(messages)
                    classes=gpt_answer.replace("\n\n","\n").split("\n")
                    if (len(classes)==1):
                        return 
                    new_dict={}
                    articles=value.split("\n")
                    print(classes)
                    for new_class in classes:
                    
                        parts=new_class.split("//")
                        new_title=parts[0]
                        numbers=parts[1].split(",")
                        new_content=""
                        for number in numbers:
                            prefix="["+number+"]"
                            for article in articles:
                                if article.startswith(prefix):
                                    new_content+=article
                                    new_content+="\n"
                        new_dict[new_title]=new_content
                    obj[key]=new_dict




def merge(obj,max_num):
    if isinstance(obj, str):
            return
    titles=list(obj.keys())
   # print(titles)
    if "others" in titles:
        titles.remove("others")
    for key,value in obj.items():
        if isinstance(value, dict):
            merge(obj[key],max_num)
    
    if(len(titles)>max_num):
        number_list = [f"[{i}]{string}" for i, string in enumerate(titles)]
        merge_prompt=f"""You will receive a lot of sub-headings related to {key}. Each sub_heading begins with a number in brackets as its serial number. Your task is to classify these sub-headings and come up with a separate heading for each class. Please output a heading and the serial number of the corresponding sub-headings on each line. The title and serial number are separated by '//', and multiple serial numbers are separated by ','. \nSample output: Output value growth//2,3,5\nGreen agriculture//0,1\nNote: 1. The output must comply with the format requirements and wrap after the serial number set of each title; 2. You can divide the sub-headings into NO MORE THAN 4 classes. \nBelow are multiple sub_headings: \n{number_list}\nPlease answer the classification results directly in the required format without any extra words."""
        messages=[{"role":"user","content":merge_prompt}]
        gpt_answer=chatgpt(messages)
        new_titles=gpt_answer.replace("\n\n","\n").split("\n")
        for title in new_titles:
            new_dict={}
            parts=title.split("//")
            new_title=parts[0]
            numbers=parts[1].split(",")
            if len(numbers)==1:
                continue
            else:
                for number in numbers:
                    num=int(number)
                    old_title=titles[num]
                    new_dict[old_title]=obj[old_title]
                    del obj[old_title]
                obj[new_title]=new_dict
    

            
def search(obj,text,num):
    titles=list(obj.keys())
    if isinstance(obj, str):
        return
    if isinstance(obj, dict):
        select_title_prompt=f"""You will receive a section heading library and a text for diabetes trials. Please follow the steps below: 1. Understand the text and find the heading that match the text from the section heading library. 2. Summarize the content from the text that is related to the heading. 3. Each output must contain two parts: 'subsection heading&&Summary content'. 4. If there is no any heading that matches the text, output 'None'. \n Sample output1: Symptoms of COVID-19&&A small number of patients with COVID-19 may experience severe headaches. \n Sample output2:  Oral medication&&The trial found that the combination of Nirmatrelvir and Ritonavir 2 was significantly better than using them separately in relieving symptoms such as breathing difficulties and severe headaches caused by COVID-19. \nNote: 1. Output must be in the required format, and only wrap after the summary content; 2. Select headings that are most related to the text, otherwise output 'None' when there is no any related heading;  \nHeading library: {titles}\nText: {text}\n\nPlease direct answer without extra words.""" 
        messages=[{"role":"user","content":select_title_prompt}]
        title=chatgpt(messages)
        print(title)
        ##生成新的标题
        if(title=="None"or "None" in title):
            summary_prompt=f"""Please generate a summary based on the text provided.\n Sample output: \n The trial found that the combination of Nirmatrelvir and Ritonavir 2 was significantly better than using them separately in relieving symptoms such as breathing difficulties and severe headaches caused by COVID-19.\nText: {text}\n\nPlease directly respond with your summary without any redundant words."""
            messages=[{"role":"user","content":summary_prompt}]
            summary=chatgpt(messages)
            summary="["+str(num)+"]"+summary+"\n"
            if("others" in titles):
                obj["others"]+=summary
            else:
                obj["others"]=summary
        else:
            title=title.replace("\n","")
            line=title.split("&&")
            name=line[0]
            summary="["+str(num)+"]"+line[1]+"\n"
            obj_=obj[name]      
            if isinstance(obj_, dict):
                search(obj[name],text,num)
            if isinstance(obj_, str):
                obj[name]+=summary

                
def merge_similar_keys(data, similarity_threshold=0.8):
    """
    遍历嵌套字典，合并字符串相似的叶子结点键的值到第一个键，并删除其他相似的键。

    :param data: 待处理的嵌套字典
    :param similarity_threshold: 相似度阈值，介于0到1之间，默认值为0.8
    """
    key_locations = {}  # 记录已处理的键及其代表键

    def are_keys_similar(key1, key2):
        # 计算两个键的相似度
        embeddings_a = model.encode(key1,convert_to_tensor=True).unsqueeze(0)
        embeddings_b = model.encode(key2,convert_to_tensor=True).unsqueeze(0)
        similarity=torch.nn.functional.cosine_similarity(embeddings_a, embeddings_b,dim=-1)
        return similarity >= similarity_threshold

    def find_representative_key(key):
        # 查找已有的相似键的代表键
        for rep_key in key_locations:
            if are_keys_similar(key, rep_key):
                print(key+","+rep_key+"\n")
                return rep_key
        return None

    def traverse(d):
        keys_to_delete = []
        for key in list(d.keys()):
            if(key=="others"):
                continue  ##跳过others
            value = d[key]
            if isinstance(value, dict):
                traverse(value)  # 递归遍历子字典
            else:
                rep_key = find_representative_key(key)
                if rep_key:
                    # 如果找到相似的代表键，合并值
                    first_parent, first_key = key_locations[rep_key]
                    first_parent[first_key] += value  # 根据需要更改合并方式
                    keys_to_delete.append(key)  # 标记当前键待删除
                else:
                    # 记录新键的首次出现位置
                    key_locations[key] = (d, key)
        # 删除标记的键
        for key in keys_to_delete:
            del d[key]

    traverse(data)

        



with open('output7/merge_800.json','r',encoding='utf-8') as g :
    directory=json.load(g)

def generate_wiki(directory, articles):
    for i in range(801,1001):
        article=articles[i]
        text=article["content"]
        num=article["id"]
    
        try:
            search(directory,text,num)
        except Exception as exc:
            error_message = f"Error: {str(exc)}"
            print(num)
            print(error_message)
            continue
            

        if(article["id"]%20==0):
            name=f"""output7/step_{article["id"]}.json"""
            with open(name, 'w') as file:
                json.dump(directory, file, indent=4)
    
            split(directory,6000)
            name1=f"""output7/split_{article["id"]}.json"""
            with open(name1, 'w') as file:
                json.dump(directory, file, indent=4)
    

            merge_similar_keys(directory, similarity_threshold=0.9)
            name3=f"""output7/unrepeat_{article["id"]}.json"""
            with open(name3, 'w') as file:
                json.dump(directory, file, indent=4)


            merge(directory,15)
            name2=f"""output7/merge_{article["id"]}.json"""
            with open(name2, 'w') as file:
                json.dump(directory, file, indent=4)
        

        
            
generate_wiki(directory, articles)
