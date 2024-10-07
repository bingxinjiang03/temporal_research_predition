from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import json
import csv
def find_keys_containing_substring(d, substring):
    matching_keys = []
    for key, value in d.items():
        if isinstance(value, dict):
            matching_keys.extend(find_keys_containing_substring(value, substring))
        elif isinstance(value, str) and substring in value:
            matching_keys.append(key)
    return matching_keys


model = SentenceTransformer('gtr-base')

with open("all_item.txt", 'r') as file:
    lines = file.readlines()  


with open('output6/merge_400_new.json','r',encoding='utf-8') as g :
    nested_dict=json.load(g)
result_all=[]

# 计算句子嵌入
embeddings_a = model.encode(lines)

with open('diabete_cot.json', 'r', encoding='utf-8') as file:
    articles = [json.loads(line) for line in file]
    


with open("data1.csv", "w", newline='') as file:
    data=["item0","title1","title2","title3","title4","title5","title6","item1_title","item1","if_find"]
    writer = csv.writer(file,delimiter='|')
    writer.writerow(data)
    file.flush()  # 立即保存
    for i in range(0,548):
        cot=articles[i]["cot"]
        cot=cot.split("  \n")
        embeddings_b = model.encode(cot)
        # 计算余弦相似度
        similarities = cosine_similarity(embeddings_b, embeddings_a)
        # 对于b中的每个句子，找到1中最相似的6个句子
        top_n = 6
        print(i)
        for i in range(len(cot)-1):
            try:
                data=[]
                data.append(cot[i])
                #找到相关的标题
                top_indices = np.argsort(similarities[i])[::-1][:top_n]
                for idx in top_indices:
                    substring = lines[idx]
                
                    result = find_keys_containing_substring(nested_dict, substring)
                    data.append(result[0])
                #找到下一个cot的标题
                top_indices = np.argsort(similarities[i+1])[::-1][:1]
                idx=top_indices[0]
                item1=lines[idx]
                item1_title=find_keys_containing_substring(nested_dict, item1)
                if item1_title[0] in data:
                    data.append(item1_title[0])
                    data.append(cot[i+1])
                    data.append("YES")
                else:
                    data.append("")
                    data.append("")
                    data.append("NO")
                writer.writerow(data)
                file.flush()  # 立即保存
            except Exception as exc:
                error_message = f"Error: {str(exc)}"
                print(error_message)

#print(result_all)

