from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import json
import csv
import torch
torch.cuda.empty_cache()
import openai

openai.api_base=""
openai.api_key=""
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


def find_keys_containing_substring(d, substring):
    matching_keys = []
    for key, value in d.items():
        if isinstance(value, dict):
            matching_keys.extend(find_keys_containing_substring(value, substring))
        elif isinstance(value, str) and substring in value:
            matching_keys.append(key)
    return matching_keys


def find_value_by_key(data, target_key):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                return value
            elif isinstance(value, (dict, list)):
                result = find_value_by_key(value, target_key)
                if result is not None:
                    return result
    elif isinstance(data, list):
        for item in data:
            result = find_value_by_key(item, target_key)
            if result is not None:
                return result
    return None  # 如果没有找到，返回 None

model = SentenceTransformer('gtr-base')

with open("all_item.txt", 'r') as file:
    lines = file.readlines()  
with open('merge_1000_no_others.json','r',encoding='utf-8') as g :
    nested_dict=json.load(g)


with open('summary_wiki_short.json','r',encoding='utf-8') as g :
    summary_dict=json.load(g)


with open('new_dic-none.json','r',encoding='utf-8') as g :
    mulu=json.load(g)


# 计算句子嵌入
embeddings_a = model.encode(lines)

articles = []
with open('diabete_cot1.json', 'r') as file:
    for line in file:
        line = line.strip()  # 去掉每一行的首尾空白字符
        if not line:  # 跳过空行
            continue
        try:
            articles.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON on line: {line}, error: {e}")    


with open("1025.json", "a", newline='') as file:
    for artitcle_id in range(760,797):
        cot=articles[artitcle_id]["cot"]
        cot=cot.split("\n")
        embeddings_b = model.encode(cot)
        # 计算余弦相似度
        similarities = cosine_similarity(embeddings_b, embeddings_a)
        # 对于b中的每个句子，找到1中最相似的10个句子
        top_n = 10
        print(artitcle_id)
        for i in range(len(cot)-1):
            try:
                data=[]
                #找到相关的标题
                top_indices = np.argsort(similarities[i])[::-1][:top_n]
                substrings=""
                for num,idx in enumerate(top_indices):                
                    substrings+=lines[idx]
                    substrings+="\n"
                similar_prompt=f"""Given a text and the other 10 texts, determine whether they discuss similar topics. If they are similar, output yes, and if they are not similar, output no. Each result is separated by a comma.
Example output:
YES,NO,YES,YES,YES,NO,NO,NO,NO,NO
text:
{cot[i]}
other 10 texts:
{substrings}"""
                messages=[{"role":"user","content":similar_prompt}]
                similar=chatgpt(messages)
                similar_count=similar.replace("\n","").split(",")
                if(("NO" in similar_count) and similar_count.count("NO")>6):
                    continue
                
                substrings=substrings.replace("\n\n","\n").split("\n")
                for num,tag in enumerate(similar_count):
                    if tag=="YES":
                        result = find_keys_containing_substring(nested_dict, substrings[num])
                        key=result[0]
                        data.append(result[0])
                
                summary_data = [find_value_by_key(summary_dict,x) for x in data]
                input1=f"""There is a known knowledge and multiple paragraphs related to it, judge whether these paragraphs contain useful information for the next step of research. If yes, output Yes, and output the paragraphs that need to be consulted in the next step. If not, output No.
known knowledge:{cot[i]}
related paragraphs:\n"""
                
                output0="("
                for ti in range(len(data)):
                    input1+=data[ti]
                    output0+=data[ti]
                    if(ti==len(data)-1):
                        output0+=")"
                    else:
                         output0+=","
                    input1+=":\n"
                    input1+=summary_data[ti]
                    input1+="\n"
                
                input0=f"""There is a known knowledge and a wiki directory related to diabetes. Output titles that may be related to this research.
                known knowledge:{cot[i]}
                directory:{mulu}"""
               # output0=data
                data_list=[]
                data_list.append(input0)
                data_list.append(output0)
                data_dic={'id':artitcle_id,'data':data_list}

                file.write(json.dumps(data_dic))
                file.write('\n')
                file.flush()

                


                #找到下一个cot的标题
                top_indices = np.argsort(similarities[i+1])[::-1][:10]        
                substrings=""
                for num,idx in enumerate(top_indices):
                    substrings+=lines[idx]
                    substrings+="\n"
                similar_prompt=f"""Given a text and the other 10 paper summaries, determine whether each paper can inspire this research idea. If can, output YES, and if can not, output NO. Each result is separated by a comma.
Example output:
NO,NO,YES,NO,NO,YES,NO,NO,NO,NO
text:
{cot[i+1]}
other 10 paper summaries:
{substrings}"""
                messages=[{"role":"user","content":similar_prompt}]
                similar=chatgpt(messages)
                print(similar)
                similar_count=similar.replace("\n","").split(",")

                if("YES" not in similar_count):
                    continue
                
                substrings=substrings.replace("\n\n","\n").split("\n")
                for num,tag in enumerate(similar_count):
                    if tag=="YES":
                        item1_title=find_keys_containing_substring(nested_dict, substrings[num])
                        break
                

                if item1_title[0] in data:
                    output1=f"""YES, {item1_title[0]}"""
                    data_list=[]
                    data_list.append(input1)
                    data_list.append(output1)
                    data_dic={'id':artitcle_id,'data':data_list}
                    file.write(json.dumps(data_dic))
                    file.write('\n')
                    file.flush()

                    input2=f"""There is a known knowledge and multiple paper summaries related to {item1_title[0]}:. Output the next research ideas based on the information in these papers.
research knowledge:
{cot[i]}
paper summaries:
{find_value_by_key(nested_dict,item1_title[0])}"""
                    output2=cot[i+1]
                    data_list=[]
                    data_list.append(input2)
                    data_list.append(output2)
                    data_dic={'id':artitcle_id,'data':data_list}

                    file.write(json.dumps(data_dic))
                    file.write('\n')
                    file.flush()

                else:
                    output1="SKIP"
                    data_list=[]
                    data_list.append(input1)
                    data_list.append(output1)
                    data_dic={'id':artitcle_id,'data':data_list}

                    file.write(json.dumps(data_dic))
                    file.write('\n')
                    file.flush()
            except Exception as exc:
                error_message = f"Error: {str(exc)}"
                print(error_message)

#print(result_all)

