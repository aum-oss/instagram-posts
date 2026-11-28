import json
T=json.load(open('timing.json'))
TEXTS=["Como tirar 12 meninos que não sabem mergulhar de uma caverna inundada?",
"Tailândia, 23 de junho de 2018. 12 meninos de um time de futebol, de 11 a 16 anos, entram numa caverna com o técnico, depois do treino. Era para ser um passeio de uma hora. Mas começa a chuva de monção. A água invade o túnel e fecha a saída. Eles vão cada vez mais fundo, fugindo da água.",
"Ninguém sabe se estão vivos. 9 dias depois, dois mergulhadores britânicos encontram os 13 numa pedra, a 4 quilômetros da entrada. Vivos.",
"Mas encontrar foi a parte fácil. Para sair, era preciso mergulhar por trechos inteiros debaixo d'água: escuros, estreitos, com lama e correnteza. Há passagens onde mal cabe uma pessoa com o cilindro.",
"E o tempo estava acabando. O oxigênio da caverna caiu para 15%. A previsão era de mais chuva. Então veio a pior notícia: Saman Kunan, ex-mergulhador da Marinha tailandesa, morreu sem ar dentro da caverna, depois de levar cilindros de oxigênio. Se um profissional morreu ali, como sairiam meninos que nunca mergulharam?",
"O plano foi um dos mais ousados da história. Um menino em pânico debaixo d'água poderia arrancar a máscara e morrer, levando o mergulhador junto. Por isso, um anestesista mergulhou até eles. Cada menino foi anestesiado, recebeu uma máscara de rosto inteiro com oxigênio, e foi levado dormindo, guiado por um mergulhador através da água.",
"De 8 a 10 de julho, um por um, os 12 meninos e o técnico saíram vivos.",
"Eles não saíram nadando. Saíram dormindo. Essa história virou filme: Treze Vidas, O Resgate, no Prime Video. Vale muito a pena. Qual resgate a gente explica no próximo? Comenta aí."]
SPOKEN={"12":"doze","23":"vinteetrês","2018":"doismiledezoito","11":"onze","16":"dezesseis","9":"nove","13":"treze","4":"quatro","15%":"quinzeporcento","8":"oito","10":"dez"}
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
