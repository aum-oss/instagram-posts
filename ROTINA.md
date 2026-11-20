# Rotina de publicação — @digitalnomad2050 (21 a 30/11/2026)

Conta Instagram via Windsor.ai: conector `instagram`, conta `17841472160483728`.
Imagens e vídeos são servidos (GitHub Pages; após o push, aguardar ~1–2 min para o arquivo ficar disponível) por `https://aum-oss.github.io/instagram-posts/<caminho>`.
Horários em Europe/Paris. Brasília = Paris − 4h.

## 1. Notícia do dia (manhã) — roda às 10h17, publica automaticamente por volta de 10h30 (6h30 Brasília)

O usuário autorizou publicar SEM aprovação prévia. Por isso a checagem de fatos é obrigatória e rígida; se nenhuma notícia passar, não publicar e avisar.

1. Pesquisar na web ataques cibernéticos / incidentes de segurança / golpes das **últimas 24–48h**.
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
3. Legenda: 2 a 4 linhas, termina com UMA ação ("Manda pra quem precisa", "Salva pra ver depois"...), 3 a 5 hashtags. Fonte citada na legenda ("Fonte: <veículo>").
4. Commit + push. Adicionar a entrada em `posts.json` (slot `manha`, status `aguardando aprovação`).
5. Publicar: `create_video_post` com `video_url`, `cover_url`, `caption`, `share_to_feed: true`.
6. Avisar o usuário (mensagem curta) com tema, fonte e que já está no ar.
7. Depois de publicar: status `publicado` + media id em `posts.json` e `POSTS.md`, commit + push.

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
