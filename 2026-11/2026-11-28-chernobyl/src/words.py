import json
T=json.load(open('timing.json'))
TEXTS=["Como apertar o botão de DESLIGAR fez um reator nuclear explodir?",
"Chernobyl, Ucrânia soviética. 26 de abril de 1986, 1h23 da manhã. O reator 4 está no meio de um teste de segurança.",
"Dentro dele, mais de 1.600 canais com urânio. A água esfria o núcleo, e as barras de controle descem para frear a reação.",
"A potência tinha caído demais. Para recuperar, os operadores puxaram quase todas as barras para fora. Sobraram só 8, quando a regra mandava ter no mínimo 15.",
"1h23 e 40 segundos. Alguém aperta o AZ-5, o botão de desligamento de emergência. Todas as barras começam a descer ao mesmo tempo.",
"Mas a ponta de cada barra era de grafite, e o grafite acelera a reação. Ao entrar, essa ponta empurrou a água para fora. Por alguns segundos, as barras esquentaram o reator, em vez de desligar.",
"A potência disparou. A água virou vapor de uma vez e arremessou a tampa de 1.000 toneladas. O botão funcionou como foi projetado. O problema era o projeto. Qual desastre a gente explica no próximo? Comenta aí."]
SPOKEN={"26":"vinteeseis","1986":"milnovecentoseoitentaeseis","1h23":"umaevinteetrês","4":"quatro","1.600":"mileseiscentos","8":"oito","15":"quinze","40":"quarenta","AZ-5":"azêcinco","1.000":"mil"}
def weight(w):
    s=w.strip(".,:;!?")
    k=len(SPOKEN.get(s,s))+2
    if w[-1] in ".!?": k+=6
    elif w[-1] in ",:": k+=3
    return k
out=[]
for txt,(a,b) in zip(TEXTS,T["speech"]):
    ws=txt.split();wt=[weight(w) for w in ws];tot=sum(wt)-6;t=a;sc=[]
    for w,k in zip(ws,wt):
        d=(b-a)*k/tot;sc.append([w,round(t,3),round(t+d,3)]);t+=d
    out.append(sc)
json.dump(out,open('words.json','w'),ensure_ascii=False)
