# Rotina de publicação — @digitalnomad2050 (21 a 30/11/2026)

Conta Instagram via Windsor.ai: conector `instagram`, conta `17841472160483728`.
Imagens e vídeos são servidos (GitHub Pages; após o push, aguardar ~1–2 min para o arquivo ficar disponível) por `https://aum-oss.github.io/instagram-posts/<caminho>`.
Horários em Europe/Paris. Brasília = Paris − 4h.

## 1. Notícia do dia (manhã) — roda às 10h17, publica automaticamente por volta de 10h30 (6h30 Brasília)

O usuário autorizou publicar SEM aprovação prévia. Por isso a checagem de fatos é obrigatória e rígida; se nenhuma notícia passar, não publicar e avisar.

1. Pesquisar na web, logo antes de publicar, ataques cibernéticos / incidentes de segurança / golpes noticiados nas **últimas horas** (desde a manhã de ontem, ~24h; o mais recente primeiro). Buscar com "hoje", "ontem" e a data do dia, em português e inglês. Só usar 24–48h se não houver nada forte nas últimas 24h; nunca mais antigo que 48h. Conferir a data de publicação na matéria aberta.
   - Fontes confiáveis: The Hacker News, BleepingComputer, SecurityWeek, The Record, Reuters, AP, CERTs/agências oficiais, comunicado da própria empresa.
   - Só fatos confirmados por pelo menos uma fonte confiável. Se algo ainda é suspeita, dizer "suspeita de". Números: usar o valor mais conservador.
   - Critério editorial: notícias FORTES e IMPORTANTES, de interesse do público em geral (não só de quem trabalha com TI).
     Prioridade: o que afeta o dia a dia das pessoas (bancos, Pix, WhatsApp, Instagram, celular, compras, serviços públicos, saúde, transporte),
     nomes conhecidos, impacto em muita gente, Brasil primeiro, depois Europa/EUA, e IA.
     Também valem ataques a instituições muito conhecidas (FBI, governos, ministérios, grandes órgãos públicos), mesmo sem impacto direto no dia a dia — o usuário pediu esse tipo de notícia em 21/11 (ex.: invasão do banco de dados criminal do FBI). Se ainda não houver confirmação oficial, dizer "suspeita de" e citar os veículos.
     Evitar: notícias técnicas de nicho (CVEs, ferramentas de empresa, falhas que só afetam servidores) a menos que mexam com o público.
   - MARCAS BRASILEIRAS PRIMEIRO (pedido do usuário em 24/11, com base nos números: FBI e WhatsApp tiveram 2x o alcance; Bell, Cleverbridge e LaLiga ficaram no fim):
     priorizar empresas e marcas que o brasileiro conhece e usa (Nubank, Itaú, Bradesco, Banco do Brasil, Caixa, Santander, Inter, PicPay, Mercado Livre/Pago, iFood, Magalu, Americanas, Shopee/Amazon Brasil, Vivo, Claro, TIM, Gov.br, INSS, Receita, SUS, Pix...).
     Marca estrangeira só se for muito usada no Brasil (WhatsApp, Instagram, Google, Apple, Netflix...) ou instituição muito conhecida (FBI etc.). Evitar empresa estrangeira que o público não reconhece.
   - Manchete (pedido do usuário em 24/11): de IMPACTO, chamativa, curta, com o NOME DA MARCA em destaque na tela 1 (ex.: "NUBANK: DADOS VAZARAM", "ALERTA PIX", "GOLPE NO GOV.BR").
     Limite fixo: a manchete é sempre verdadeira. Nada de inventar, aumentar número, dizer "confirmado" quando é suspeita ou prometer perigo que não existe.
     Sem piada com vítimas. Explicar em linguagem simples, sem jargão, e sempre terminar com o que a pessoa comum pode fazer para se proteger.
   - Não repetir tema já listado em `POSTS.md`.
2. Criar um reel no padrão do perfil com `tools/render.py` (tag `ATAQUE DO DIA`):
   cenas = hook (frase curta + destaque) → 2 a 3 itens com o que aconteceu → `tip` "O que fazer:" → `cta`.
   Salvar o JSON em `2026-11/<AAAA-MM-DD>-noticia/post.json` e gerar em `2026-11/<AAAA-MM-DD>-noticia/`.
   Rodar: `python3 tools/render.py 2026-11/<pasta>/post.json 2026-11/<pasta>`.
   Tela 1 (gancho) é curta, ~3 s (pedido do usuário em 24/11: muita gente pulava nos 3 primeiros segundos). Máx. ~6 palavras na linha vermelha.
   Ritmo: o padrão do render.py é `pace` 1.75 (pedido do usuário em 22/11: ~30% mais rápido que o 2.25 anterior; título ~5,5s, cada item ~5,5s, "O que fazer" ~7s). Não definir `pace` no post.json nem acelerar.
3. Datas (pedido do usuário em 21/11): sempre situar o público no tempo. No vídeo, a data do ataque/divulgação aparece já no gancho ou no item 1 (ex.: "em 14/11"); na legenda, a primeira linha diz quando aconteceu e quando foi divulgado (dia/mês).
   Legenda: 2 a 4 linhas, termina com UMA ação ("Manda pra quem precisa", "Salva pra ver depois"...), 3 a 5 hashtags. Fonte citada na legenda ("Fonte: <veículo>").
4. Commit + push. Adicionar a entrada em `posts.json` (slot `manha`, status `aguardando aprovação`).
5. Publicar: `create_video_post` com `video_url`, `cover_url`, `caption`, `share_to_feed: true`.
6. Avisar o usuário (mensagem curta) com tema, fonte e que já está no ar.
7. Depois de publicar: status `publicado` + media id em `posts.json` e `POSTS.md`, commit + push.

## 1b. Varreduras de notícia urgente — 12h13 e 15h47 (Brasília), publica só se houver algo forte

Objetivo: noticiar ataques recentes entre os primeiros, sem lotar o feed. A maioria das varreduras deve terminar SEM publicar.
- Publicar só se TODOS forem verdade:
  1. noticiado nas últimas ~6–8h (conferir a data/hora na matéria aberta);
  2. impacto grande no público geral (banco, Pix, WhatsApp, app conhecido, governo, saúde, transporte...);
  3. confirmado pela empresa, por órgão oficial ou por 2 veículos grandes (alegação só de hackers não serve);
  4. tema não publicado antes em `POSTS.md` (salvo novidade relevante, como número novo de afetados);
  5. ainda não houve nenhuma notícia extra hoje (slot `extra` em `posts.json` com data de hoje) — máximo 1 extra por dia.
- Mesmo padrão do item 1 (reel `ATAQUE DO DIA`, datas no vídeo e na legenda, fonte na legenda, pace padrão). Pasta `2026-11/<AAAA-MM-DD>-urgente`, slot `extra`.
- Se não publicar, não avisar o usuário.

## 2. Post de dica (noite) — 23h00 Paris (19h Brasília)

Publicar a entrada de `posts.json` com `slot: noite` e data de hoje **somente se** `status` = `aprovado`.
- reel → `create_video_post` (`video_url`, `cover_url`, `caption`; se `trial` = true, `trial_params: {graduation_strategy: SS_PERFORMANCE}`)
  - Se o Instagram recusar o trial reel por falta de seguidores ("zu wenige Follower" / poucos seguidores), publicar de novo como reel normal (sem `trial_params`), marcar `trial: false` e anotar no POSTS.md e na mensagem final que saiu como reel normal.
- carousel → `create_carousel_post` (`image_urls`, `caption`)
Depois: status `publicado` + media id, atualizar `POSTS.md`, commit + push.
Se não houver post aprovado para hoje, não publicar nada.

## Regras gerais
- Nunca publicar nada que não esteja aprovado.
- Nunca apagar posts nem responder comentários automaticamente.
- Commits terminam com:
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`

## Banco de ganchos (primeira tela do reel — escolha e adapte)
Regra: o gancho aparece já no primeiro quadro, curto (máx. 8 palavras na linha de destaque), sem exagero nem mentira.
1. "Isso aconteceu ontem e pode afetar você."
2. "Se você usa [app/banco], preste atenção."
3. "[X] milhões de pessoas tiveram dados expostos."
4. "Esse golpe está pegando muita gente agora."
5. "Seu [WhatsApp/Pix/celular] pode ser o próximo."
6. "Ninguém te avisou disso sobre [IA/Pix/WhatsApp]."
7. "Pare de fazer isso com sua senha."
8. "Parece real, mas é golpe."
9. "Os hackers não invadiram. Alguém abriu a porta."
10. "Uma mensagem. Foi só isso que precisou."
11. "A IA agora está do lado dos golpistas também."
12. "Se recebeu essa mensagem, não clique."
13. "O que fazer se seus dados vazaram (em 30s)."
14. "A empresa só contou semanas depois."
15. "Isso não é filme: aconteceu esta semana."
16. "3 sinais de que você caiu nesse golpe."
17. "Até [empresa grande] caiu nessa."
18. "Seu banco nunca vai te pedir isso."
19. "Você tem 1 minuto? Proteja sua conta agora."
20. "O golpe mudou. Veja como ele funciona hoje."

## Palavras-chave (busca do Instagram)
Usar no texto do vídeo E na legenda o termo que as pessoas digitam na busca:
"golpe do Pix", "WhatsApp clonado", "vazamento de dados", "senha vazada", "golpe no Instagram", "golpe com IA", "dados vazados", "conta hackeada".

## 4. Story diário: roda às 18h43 Paris (14h43 Brasília), publica sem aprovação (pedido do usuário em 24/11)

Objetivo: ter story todo dia (círculo colorido na foto) e alimentar os destaques "Ataques Reais", "Golpes" e "Dicas".
1. Em `posts.json`, pegar a entrada de HOJE (data de `publish_at`, horário de Paris) com status `publicado` e `type` `reel`. Preferir slot `serie`; senão `manha`; senão `urgente`. Se não houver nenhuma, não publicar e encerrar sem avisar.
2. Baixar o vídeo do próprio repositório (arquivo `reel.mp4` da pasta) e medir a duração com ffprobe. Story aceita de 3 a 60 s: se passar de 59 s, cortar com `ffmpeg -t 59 -c:v libx264 -preset veryfast -crf 20 -c:a aac` e salvar `story.mp4` na mesma pasta, commit + push e esperar ~2 min o GitHub Pages.
3. Publicar com `create_story` (só `video_url`, sem legenda).
4. Registrar na entrada do `posts.json` o campo `story_media_id`, commit + push.
5. Não mandar mensagem ao usuário se der certo; só avisar se falhar.
