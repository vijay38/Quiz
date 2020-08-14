from django.shortcuts import render
from .forms import UserForm
from django.http import HttpResponse
import os
import dotenv
import random
from pymongo import MongoClient
import pandas as pd
import pdfkit
dotenv.load_dotenv()

def user(request):
    client=MongoClient(os.getenv("mongolink"))
    mongodb=client.get_database("Quiz")
    mongocoll=mongodb.param
    l=list(mongocoll.find({}))
    if l[0]["status"]==False:
        client.close()
        return render(request,"ended.html")
    form=UserForm()
    client.close()
    return render(request,'login.html',{'form':form})
def quiz(request):
    client=MongoClient(os.getenv("mongolink"))
    mongodb=client.get_database("Quiz")
    mongocoll=mongodb.users
    phone=request.POST["user"]
    l=list(mongocoll.find({"phone":phone}))
    qn=l[0]["ques"]
    order=list(map(int,l[0]["order"].split(" ")))
    mongocoll=mongodb.param
    l=list(mongocoll.find({}))
    timer=l[0]["time"]
    mongocoll=mongodb.questions
    l=list(mongocoll.find({"qnum":order[qn-1]},{"_id":0}))
    data={"time":timer,"quest":l[0]["question"].decode("utf-8")}
    data["a"]=l[0]["a"].decode("utf-8")
    data["b"]=l[0]["b"].decode("utf-8")
    data["c"]=l[0]["c"].decode("utf-8")
    data["d"]=l[0]["d"].decode("utf-8")
    data["qnum"]=qn
    data["id"]=phone
    client.close()
    return render(request,"questions.html",data)
def next(request):
    client=MongoClient(os.getenv("mongolink"))
    mongodb=client.get_database("Quiz")
    mongocoll=mongodb.param
    l=list(mongocoll.find({}))
    timer=l[0]["time"]
    max_num=l[0]["num"]
    status=l[0]["status"]
    if status==False:
        client.close()
        return render(request,"ended.html")
    mongocoll=mongodb.users
    l=list(mongocoll.find({"phone":request.POST["user"]}))
    qn=l[0]["ques"]
    st=l[0]["completed"]
    st1=l[0]["wrong"]
    st2=l[0]["wrongop"]
    prev_score=l[0]["score"]
    prev_correct=l[0]["correct"]
    prev_time=l[0]["time"]
    order=list(map(int,l[0]["order"].split(" ")))
    mongocoll=mongodb.questions
    try:
        l=list(mongocoll.find({"qnum":order[qn-1]}))
        actual=l[0]["ans"]
    except Exception:
        return HttpResponse("<h1 style='text-align: center;'>Thanks for Participating</h1>")
    actual=actual.decode("utf-8")
    actual=actual.lower()
    mongocoll=mongodb.users
    if not str(request.POST["number"]) in st.split(" "):
        secs=int(request.POST["secs"])
        op=request.POST["ans"]
        if actual==op:
            score=secs+600
            correct=prev_correct+1
            mongocoll.update_one({"phone":request.POST["user"]},{"$set":{"score":score+prev_score,"ques":qn+1,"correct":prev_correct+1,"time":timer-secs+prev_time,"completed":st+" "+str(qn)}})
        else:
            score=0
            correct=prev_correct
            mongocoll.update_one({"phone":request.POST["user"]},{"$set":{"ques":qn+1,"wrong":st1+" "+str(qn),"completed":st+" "+str(qn),"wrongop":st2+" "+op}})
        if qn+1==max_num:
            return render(request,"score.html",{"score":score+prev_score,"time":timer-secs+prev_time,"correct":correct})
        mongocoll=mongodb.questions
        l=list(mongocoll.find({"qnum":order[qn]},{"_id":0}))
        data={"time":timer,"quest":l[0]["question"].decode("utf-8")}
        data["a"]=l[0]["a"].decode("utf-8")
        data["b"]=l[0]["b"].decode("utf-8")
        data["c"]=l[0]["c"].decode("utf-8")
        data["d"]=l[0]["d"].decode("utf-8")
        data["qnum"]=qn+1
        data["id"]=request.POST["user"]
        client.close()
    else:
        mongocoll=mongodb.questions
        l=list(mongocoll.find({"qnum":order[qn-1]},{"_id":0}))
        data={"time":timer,"quest":l[0]["question"].decode("utf-8")}
        data["a"]=l[0]["a"].decode("utf-8")
        data["b"]=l[0]["b"].decode("utf-8")
        data["c"]=l[0]["c"].decode("utf-8")
        data["d"]=l[0]["d"].decode("utf-8")
        data["qnum"]=qn
        data["id"]=request.POST["user"]
        client.close()
    return render(request,"questions.html",data)
def admin(request):
    return render(request,"admin.html")
def edit(request):
    if "a" in request.POST:
        ques=request.POST["ques"]
        a=request.POST["a"]
        b=request.POST["b"]
        c=request.POST["c"]
        d=request.POST["d"]
        ans=request.POST["ans"]
        client=MongoClient(os.getenv("mongolink"))
        mongodb=client.get_database("Quiz")
        mongocoll=mongodb.questions
        l=list(mongocoll.find({"question":ques.encode("utf-8")}))
        if len(l)==0 and ques!="":
            mongocoll=mongodb.param
            qnum_list=list(mongocoll.find({}))
            qnum=qnum_list[0]["num"]
            mongocoll.update_one({"num":qnum},{"$set":{"num":qnum+1}})
            mongocoll=mongodb.questions
            que={"qnum":qnum,"question":ques.encode("utf-8"),"a":a.encode("utf-8"),"b":b.encode("utf-8"),"c":c.encode("utf-8"),"d":d.encode("utf-8"),"ans":ans.encode("utf-8")}
            mongocoll.insert_one(que)
        mongocoll=mongodb.param
        l=list(mongocoll.find({}))
        timer=l[0]["time"]
        if l[0]["status"]==True:
            data={"status":False}
        else:
            data={"status":True}
        data["timer"]=timer
        client.close()
        return render(request,'useredit.html',data)
    elif "username" in request.POST:
        user=request.POST["username"]
        pas=request.POST["password"]
        user=user.lower()
        if user==os.getenv("email") and pas==os.getenv("password"):
            client=MongoClient(os.getenv("mongolink"))
            mongodb=client.get_database("Quiz")
            mongocoll=mongodb.param
            l=list(mongocoll.find({}))
            timer=l[0]["time"]
            if l[0]["status"]==True:
                data={"status":False}
            else:
                data={"status":True}
            data["timer"]=timer
            client.close()
            return render(request,'useredit.html',data)
        else:
            return HttpResponse("<h1  style='text-align: center;'>INVALID CREDENTIALS</h1><h2 style='text-align: center;'>Try again</h2>")
    else:
        return HttpResponse("<h1  style='text-align: center;'>Please Login</h1>")
def change(request):
    client=MongoClient(os.getenv("mongolink"))
    mongodb=client.get_database("Quiz")
    mongocoll=mongodb.param
    l=list(mongocoll.find({}))
    timer=l[0]["time"]
    st=request.POST["st"]
    if st=="Stop":
        mongocoll.update_one({"status":True},{"$set":{"status":False}})
        data={"status":True}
    else:
        mongocoll.update_one({"status":False},{"$set":{"status":True}})
        data={"status":False}
    data["timer"]=timer
    client.close()
    return render(request,"useredit.html",data)
def set_timer(request):
    client=MongoClient(os.getenv("mongolink"))
    mongodb=client.get_database("Quiz")
    mongocoll=mongodb.param
    mongocoll.update_one({},{"$set":{"time":int(request.POST["timer"])}})
    l=list(mongocoll.find({}))
    if l[0]["status"]==True:
        data={"status":False}
    else:
        data={"status":True}
    timer=l[0]["time"]
    data["timer"]=timer
    return render(request,'useredit.html',data)
def result(request):
    #if "result" in request.POST:
    client=MongoClient(os.getenv("mongolink"))
    mongodb=client.get_database("Quiz")
    mongocoll=mongodb.users
    l=list(mongocoll.find({},{"_id":0}).sort("score",-1))
    for i in range(len(l)):
        d=l[i]
        d["rank"]=i+1
        d["name"]=d["name"].decode('utf-8')
        d["place"]=d["place"].decode('utf-8')
        l[i]=d
    data={"l":l}
    return render(request,"result.html",data)
    #return HttpResponse("<h1  style='text-align: center;'>Please Login</h1>")
def wrongdisp(request,phone):
    client=MongoClient(os.getenv("mongolink"))
    mongodb=client.get_database("Quiz")
    mongocoll=mongodb.users
    l=list(mongocoll.find({"phone":phone},{"wrong":1,"order":1}))
    wrong=l[0]["wrong"]
    wrong=list(map(int,wrong.split(" ")))
    wrong.pop(0)
    wrongop=l[0]["wrongop"]
    wrongop=wrongop.split(" ")
    wrongop.pop(0)
    order=l[0]["order"]
    order=list(map(int,order.split(" ")))
    data={}
    mongocoll=mongodb.questions
    l=list(mongocoll.find({}).sort("qnum"))
    client.close()
    ret=[]
    for i in range(len(wrong)):
        qnum=order[wrong[i]-1]
        question=l[qnum-1]["question"]
        option=l[qnum-1]["ans"].decode("utf-8")
        answer=l[qnum-1][option.lower()]
        if wrongop[i] not in ["a","b","c","d"]:
            wans="Not Answered"
        else:
            wans=l[qnum-1][wrongop[i]]
        ret.append({"question":question.decode("utf-8"),"answer":answer.decode("utf-8"),"wrongans":wans.decode('utf-8')})
    data["data"]=ret
    return render(request,"wrongdisp.html",data)
def instructions(request):
    form=UserForm(request.POST)
    if form.is_valid():
        name=form.cleaned_data['Name']
        place=form.cleaned_data['Place']
        phone=form.cleaned_data['Phone']
        client=MongoClient(os.getenv("mongolink"))
        mongodb=client.get_database("Quiz")
        mongocoll=mongodb.param
        l=list(mongocoll.find({}))
        que=l[0]["num"]
        display=l[0]["display"]
        choices=list(range(1,que))
        random.shuffle(choices)
        choices=list(map(str,choices))
        order=" ".join(choices)
        mongocoll=mongodb.users
        l=list(mongocoll.find({"phone":phone}))
        if len(l)>0:
            if l[0]["ques"]>=que:
                client.close()
                if display==False:
                    return render(request,"already.html")
                else:
                    return wrongdisp(request,phone)
        else:
            ins={"name":name.encode("utf-8"),"place":place.encode("utf-8"),"phone":phone,"ques":1,"correct":0,"time":0,"score":0,"completed":"0","order":order,"wrong":"0","wrongop":"0"}
            mongocoll.insert_one(ins)
        data={"id":phone}
        client.close()
        return render(request,"instruction.html",data)
    return HttpResponse("<center><h1>Invalid Phone Number</h1></center>")
def excel(request):
    client=MongoClient(os.getenv("mongolink"))
    mongodb=client.get_database("Quiz")
    mongocoll=mongodb.param
    l=list(mongocoll.find({}))
    client.close()
    url = l[0]["url"]+"admin/result"
    table = pd.read_html(url)[0]
    table.to_excel("./static/documents/data.xlsx")
    return render(request,"downloade.html")
def pdf(request):
    client=MongoClient(os.getenv("mongolink"))
    mongodb=client.get_database("Quiz")
    mongocoll=mongodb.param
    l=list(mongocoll.find({}))
    client.close()
    url = l[0]["url"]+"admin/result"
    options = {
    'page-size': 'A4',
    'margin-top': '0.25in',
    'margin-right': '0.25in',
    'margin-bottom': '0.25in',
    'margin-left': '0.25in',
    'no-outline': None
    }
    pdfkit.from_url(url,"./static/documents/data.pdf",options=options)
    return render(request,"downloadp.html")
