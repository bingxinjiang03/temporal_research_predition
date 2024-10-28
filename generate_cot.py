import json
import openai
openai.api_base = ""
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



def read_file_all_content(filename):
    with open(filename, 'r') as file:
        content = file.read()
    return content

with open('diabetes_content.json', 'r', encoding='utf-8') as file:
    articles = [json.loads(line) for line in file]


count=0
with open("diabete_cot.json", "a") as file:
    for i in range(514,1000):
        content=articles[i]["content"]
        skip_prompt=f"""Given an abstract of a paper, determine whether the abstract contains background knowledge or an introduction. If so, output YES; if not, output NO. 
    Here is the abstract:{content}"""
        messages=[{"role":"user","content":skip_prompt}]
        skip_content=chatgpt(messages)
        if(skip_content=="NO"):
            count+=1
            continue
        filter_prompt=f"""Given an abstract of a paper, delete the detailed experimental methods and only keep the Introduction, background knowledge, Objective
##example:
abstract:
[130] Type 2 diabetes and dyslipidemia are diseases that collectively increase the risk of patients developing cardiovascular complications. Several incretin-based drugs are reported to improve lipid metabolism, and one of these medications, anagliptin, is a dipeptidyl peptidase-4 (DPP-4) inhibitor that has been shown to decrease serum triglyceride and low-density lipoproteins cholesterol. This study aimed to conduct an investigation into the effects of anagliptin on serum lipid profiles. This multicenter, open-label, randomized (1:1), parallel group study was designed to evaluate the effects of anagliptin on serum lipid profiles (triglycerides, lipoproteins, apolipoproteins, and cholesterol fractions). The study involved 24 patients with type 2 diabetes at two participating hospitals for a period of 24 weeks. Patients were randomly assigned to the anagliptin (n = 12) or control (n = 12) groups. Patients in the anagliptin group were treated with 200 mg of the drug twice daily. Patients in the control group did not receive anagliptin, but continued with their previous treatment schedules. Lipid metabolism was examined under fasting conditions at baseline and 24 weeks. Patients treated with anagliptin for 24 weeks exhibited significantly reduced levels of serum apolipoprotein B-48, a marker for lipid transport from the intestine, compared with the control group patients (P < 0.05). After 24 weeks of treatment, serum adiponectin levels were significantly raised, whereas glycated hemoglobin (HbA1c) levels were significantly lower compared with the baseline in the anagliptin group (P < 0.05), but not in the control group. This study showed that the DPP-4 inhibitor anagliptin reduces fasting apolipoprotein B-48 levels, suggesting that this drug may have beneficial effects on lipid metabolism possibly mediated by the inhibition of intestinal lipid transport
output:
Type 2 diabetes and dyslipidemia are diseases that collectively increase the risk of patients developing cardiovascular complications. Several incretin-based drugs are reported to improve lipid metabolism, and one of these medications, anagliptin, is a dipeptidyl peptidase-4 (DPP-4) inhibitor that has been shown to decrease serum triglyceride and low-density lipoproteins cholesterol. This multicenter, open-label, randomized (1:1), parallel group study was designed to evaluate the effects of anagliptin on serum lipid profiles (triglycerides, lipoproteins, apolipoproteins, and cholesterol fractions). 
Here is the abstract:{content}
    Please directly respond without any redundant words."""
        messages=[{"role":"user","content":filter_prompt}]
        filtered_content=chatgpt(messages)
        cot_prompt=f"""I will provide the abstract of a research paper. Based on this abstract, Extract key information related to diabete research from the abstract in order.  
##example:
abstract:
Severe hypoglycaemia (SH) is one of the most feared complications of type 1 diabetes (T1DM) with a reported prevalence of nearly 40%. In randomized trials of Multiple Daily Injections (MDI) and Continuous Subcutaneous Insulin Infusion (CSII) therapy there is a possible benefit of CSII in reducing SH. However few trials have used basal insulin analogues as the basal insulin in the MDI group and individuals with established SH have often been excluded from prospective studies. In published studies investigating the effect of Real Time Continuous Glucose Monitoring (RT-CGM) benefit in terms of reduced SH has not yet been demonstrated. The primary objective of this study is to elucidate whether in people with T1DM complicated by impaired awareness of hypoglycaemia (IAH), rigorous prevention of biochemical hypoglycaemia using optimized existing self-management technology and educational support will restore awareness and reduce risk of recurrent SH.
output:
Severe hypoglycaemia is one of the complications for type 1 diabetes; 
Diabetes treatments include Multiple Daily Injections, Continuous Subcutaneous Insulin Infusion, Continuous Glucose Monitoring, and so on; 
Among the treatments, Multiple Daily Injections and Continuous Subcutaneous Insulin Infusion are proven to help reduce the complication, severe hypoglycaemia.
Here is the abstract:{filtered_content}"""
        messages=[{"role":"user","content":cot_prompt}]
        cot=chatgpt(messages)
        cot=cot.replace("\n\n","\n")
        articles[i]["cot"]=cot
        file.write(json.dumps(articles[i]))
        file.write('\n')
        file.flush()  # 确保每次写入后立即保存

print(count)
