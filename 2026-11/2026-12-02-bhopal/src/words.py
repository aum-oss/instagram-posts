import json
T=json.load(open('timing.json'))
TEXTS=["Como um pouco de água matou milhares de pessoas em uma noite?",
"Bhopal, Índia. 2 de dezembro de 1984. Uma fábrica de pesticidas, cercada por bairros pobres, onde milhares de famílias dormem.",
"Num tanque, 42 toneladas de isocianato de metila, um líquido muito tóxico. Se encostar em água, ele esquenta, ferve e vira gás.",
"Mas a fábrica estava largada. A refrigeração do tanque estava desligada. O lavador de gás, fora de serviço. E a chama que queimaria um vazamento, em manutenção.",
"Naquela noite, durante uma limpeza de canos, a água entrou no tanque.",
"A reação começa. O tanque passa de 200 graus, a válvula de segurança abre, e cerca de 30 toneladas de gás escapam em mais ou menos uma hora.",
"O gás é mais pesado que o ar. Ele desce sobre as casas, enquanto a cidade dorme. O alarme tocou só por alguns instantes.",
"Mais de 500 mil pessoas foram expostas. Milhares morreram. Não foi uma falha só: todas as proteções estavam desligadas ao mesmo tempo. Esse desastre foi sugerido por um seguidor. Qual a gente explica no próximo? Comenta aí."]
SPOKEN={"2":"dois","1984":"milnovecentoseoitentaequatro","42":"quarentaeduas","200":"duzentos","30":"trinta","500":"quinhentas"}
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
