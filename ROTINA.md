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
     Evitar: notícias técnicas de nicho (CVEs, ferramentas de empresa, falhas que só afetam servidores) a menos que mexam com o público.
   - Tom: sério, respeitoso e útil. Sem sensacionalismo, sem medo exagerado, sem piada com vítimas ou empresas atingidas.
     Explicar em linguagem simples, sem jargão, e sempre terminar com o que a pessoa comum pode fazer para se proteger.
   - Não repetir tema já listado em `POSTS.md`.
2. Criar um reel no padrão do perfil com `tools/render.py` (tag `ATAQUE DO DIA`):
   cenas = hook (frase curta + destaque) → 2 a 3 itens com o que aconteceu → `tip` "O que fazer:" → `cta`.
   Salvar o JSON em `2026-11/<AAAA-MM-DD>-noticia/post.json` e gerar em `2026-11/<AAAA-MM-DD>-noticia/`.
   Rodar: `python3 tools/render.py 2026-11/<pasta>/post.json 2026-11/<pasta>`.
   Ritmo: o padrão do render.py é `pace` 1.5 (cada tela fica 50% mais tempo; pedido do usuário em 21/11). Não acelerar.
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
