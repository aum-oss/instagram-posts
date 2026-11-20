# Rotina de publicação — @digitalnomad2050 (21 a 30/11/2026)

Conta Instagram via Windsor.ai: conector `instagram`, conta `17841472160483728`.
Imagens e vídeos são servidos por `https://raw.githubusercontent.com/aum-oss/instagram-posts/main/<caminho>`.
Horários em Europe/Paris. Brasília = Paris − 4h.

## 1. Notícia do dia (manhã) — preparar às ~9h, publicar às 10h40 (6h40 Brasília)

1. Pesquisar na web ataques cibernéticos / incidentes de segurança / golpes das **últimas 24–48h**.
   - Fontes confiáveis: The Hacker News, BleepingComputer, SecurityWeek, The Record, Reuters, AP, CERTs/agências oficiais, comunicado da própria empresa.
   - Só fatos confirmados por pelo menos uma fonte confiável. Se algo ainda é suspeita, dizer "suspeita de". Números: usar o valor mais conservador.
   - Preferir: nomes conhecidos (big techs, bancos, apps populares), impacto em pessoas comuns, Brasil/Europa, IA.
   - Não repetir tema já listado em `POSTS.md`.
2. Criar um reel no padrão do perfil com `tools/render.py` (tag `ATAQUE DO DIA`):
   cenas = hook (frase curta + destaque) → 2 a 3 itens com o que aconteceu → `tip` "O que fazer:" → `cta`.
   Salvar o JSON em `2026-11/<AAAA-MM-DD>-noticia/post.json` e gerar em `2026-11/<AAAA-MM-DD>-noticia/`.
   Rodar: `python3 tools/render.py 2026-11/<pasta>/post.json 2026-11/<pasta>`.
3. Legenda: 2 a 4 linhas, termina com UMA ação ("Manda pra quem precisa", "Salva pra ver depois"...), 3 a 5 hashtags. Fonte citada na legenda ("Fonte: <veículo>").
4. Commit + push. Adicionar a entrada em `posts.json` (slot `manha`, status `aguardando aprovação`).
5. **Pedir aprovação**: enviar notificação push ao usuário com o tema, a legenda e o link do vídeo; perguntar "Posso publicar às 10h40?".
6. Só publicar depois do "ok" do usuário. Se o ok vier antes das 10h40, agendar a publicação para 10h40 nesta mesma sessão; se vier depois, publicar na hora.
   Ação: `create_video_post` com `video_url`, `cover_url`, `caption`.
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
