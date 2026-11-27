import json
T=json.load(open('timing.json'))
TEXTS=["Essa máquina tinha 159 quintilhões de combinações. E mesmo assim, foi quebrada.",
"Era a Enigma, usada pelos nazistas na Segunda Guerra. Olha o que acontece quando você aperta uma tecla.",
"O sinal passa pelos cabos, atravessa três rotores, bate no refletor e volta por outro caminho. O A virou G.",
"Aperta A de novo. O rotor girou, e agora sai outra letra. Cada tecla mudava a máquina.",
"Mas tinha uma falha. Por causa do refletor, uma letra nunca virava ela mesma.",
"Os poloneses quebraram a Enigma em 1932. Depois, Alan Turing criou a Bombe, uma máquina que testava milhares de posições até achar a certa.",
"A matemática venceu a máquina. Segue pra mais curiosidades assim."]
SPOKEN={"159":"cento e cinquenta e nove","1932":"mil novecentos e trinta e dois"}
def weight(w):
    s=w.strip(".,:;!?")
    k=len(SPOKEN.get(s,s).replace(" ",""))+2
    if w[-1] in ".!?": k+=5   # pausa
    elif w[-1] in ",:": k+=3
    return k
out=[]
for txt,(a,b) in zip(TEXTS,T["speech"]):
    ws=txt.split();wt=[weight(w) for w in ws];tot=sum(wt);t=a;sc=[]
    for w,k in zip(ws,wt):
        d=(b-a)*k/tot;sc.append([w,round(t,3),round(t+d,3)]);t+=d
    out.append(sc)
json.dump(out,open('words.json','w'),ensure_ascii=False)
for sc in out: print(" ".join(f"{w}@{s}" for w,s,e in sc))
