# MCP TCE-PR — 0.3.0

Servidor comunitário Python/FastMCP para navegar pelo **portal público do TCE-PR**,
ler páginas com JavaScript e documentos, consultar processos e formulários públicos,
PIT, novo Mural e bases CSV tradicionais. Sem vínculo oficial com o tribunal.

São **19 ferramentas**, com organização modular inspirada no
[MCP Brasil](https://github.com/Mcp-Brasil/mcp-brasil) e adaptador `FeatureMeta`.

## Como funciona, em poucas palavras

Você faz uma pergunta no seu assistente de IA. O assistente chama uma ferramenta
MCP, este servidor consulta o portal do TCE-PR e devolve os resultados com a fonte.
A IA então pode explicar os dados para você. O MCP roda no seu computador;
precisa de internet e não exige chave de API do TCE-PR para as fontes públicas.
Os resultados enviados à IA seguem as condições de privacidade do cliente escolhido.

Exemplos de pedidos: “Liste as áreas do portal”, “Consulte as obras de Curitiba”,
“Pesquise um processo pelo protocolo” ou “Atualize a base de obras antes da consulta”.

## Vantagens

- Consulta páginas, documentos e bases estruturadas pela mesma conexão MCP.
- Acesso às fontes oficiais com URLs e metadados para conferir os resultados.
- Leitura parcial de ZIPs grandes, sem precisar baixar o arquivo inteiro.
- Cache limitado em memória, atualização automática nas consultas e atualização forçada.
- Código aberto sob MIT, testes incluídos e adaptação para o MCP Brasil.

## Instalação passo a passo

1. Instale [Python 3.11 ou superior](https://www.python.org/downloads/) e
   [uv](https://docs.astral.sh/uv/getting-started/installation/).
2. Baixe o ZIP pelo botão **Code → Download ZIP** e extraia, ou clone:

```sh
git clone https://github.com/Booknando/mcp-tce-pr.git
cd mcp-tce-pr
```

3. Abra um terminal na pasta extraída e execute os comandos abaixo.

## Executar

Requer Python 3.11+ e uv. Dentro desta pasta:

```sh
uv sync --locked --extra navegador
uv run --extra navegador playwright install chromium
uv run --extra navegador mcp-tce-pr
```

O transporte padrão é **stdio**. A renderização tenta Chromium e depois Edge/Chrome
instalados, sempre com perfil temporário sem cookies e credenciais do usuário.
Se Edge/Chrome já estiver disponível, a instalação do Chromium pode ser dispensada.
`MCP_TCE_BROWSER_CHANNEL=msedge` ou `chrome` define a primeira opção.

4. Adicione a configuração abaixo ao seu cliente MCP compatível com **stdio**.
   Troque `C:/caminho/mcp-tce-pr` pelo caminho absoluto da pasta extraída.
   No macOS/Linux, use por exemplo `/Users/seuusuario/mcp-tce-pr`.
   Preserve outros servidores já configurados. Se `uv` não for encontrado, use
   o caminho completo do executável no campo `command`.
5. Reinicie o cliente e peça: “Use tce-pr para listar as áreas do portal”.

Configuração para clientes que usam `mcpServers`:

```json
{
  "mcpServers": {
    "tce-pr": {
      "command": "uv",
      "args": ["run", "--directory", "C:/caminho/mcp-tce-pr", "--extra", "navegador", "mcp-tce-pr"],
      "env": {"MCP_TCE_CACHE_SECONDS": "3600"}
    }
  }
}
```

HTTP local opcional, sem autenticação:

```sh
uv run --extra navegador python -c "from mcp_tce_pr.server import mcp; mcp.run(transport='http', host='127.0.0.1', port=8000)"
```

## Atualização dos dados

**Sim: o servidor busca os dados oficiais durante o uso.** Não distribui uma cópia
congelada do portal. Existem três comportamentos:

| Fonte | Quando é consultada novamente |
|---|---|
| CSVs tradicionais e seus catálogos | Na primeira consulta após vencer o cache (padrão: 1 hora) |
| Páginas, documentos, PIT e novo Mural | A cada chamada, sem cache de conteúdo no MCP |
| `atualizar_dados_pr` | Imediatamente: baixa novamente catálogo e CSV escolhido, ignorando o cache |

Exemplo de atualização forçada: `{"base":"obras"}`. Para bases anuais:
`{"base":"acordaos","ano":2026}`. A resposta traz uma amostra e `obtido_em`,
`ultima_modificacao_http`, `etag` e `cache`, quando aplicáveis. Se a atualização
falhar, a ferramenta retorna erro; não apresenta cache antigo como dado novo.

Configure `MCP_TCE_CACHE_SECONDS` no bloco `env`: `300` para cinco minutos,
`3600` para uma hora ou `0` para consultar sempre a origem. Aceita de 0 a 86400
segundos. Reinicie o servidor após mudar essa configuração. O cache é temporário,
limitado e individual por processo; desaparece quando o servidor fecha.

**Não há varredura nem sincronização em segundo plano.** Sem consultas, o servidor
não baixa nada. Atualizar significa obter a versão que o TCE-PR disponibiliza:
se o órgão não publicar uma versão nova, o resultado pode continuar igual.
`obtido_em` é o horário da coleta, não a data de atualização de cada registro.
O próprio site/CDN pode servir conteúdo em cache, fora do controle deste MCP.

### Atualizar o programa

Dados e código são coisas diferentes. Para receber melhorias do programa, encerre
o cliente MCP, execute na pasta do projeto e depois reinicie o cliente:

```sh
git pull --ff-only
uv sync --locked --extra navegador
```

Se instalou por ZIP, baixe a nova versão, extraia em uma nova pasta e ajuste o
caminho do cliente. Não existe atualização automática do código.

## Ferramentas

| Ferramenta | Função |
|---|---|
| `listar_areas_portal_pr` | 22 pontos de entrada; siga links para outras áreas |
| `ler_pagina_portal_pr` | Texto, links, iframes e formulários de URLs públicas TCE-PR |
| `buscar_no_portal_pr` | Busca por navegação, até 30 páginas e escopo explícito |
| `ler_documento_pr` | PDF, DOCX, XLSX, CSV, JSON, XML e texto |
| `consultar_processo_pr` | Consulta pública por protocolo |
| `consultar_formulario_pr` | Formulários cadastrados de processos, sanções e inadimplentes |
| `ler_novo_mural_pr` | Navegação nas seções do Power BI do novo Mural |
| `consultar_novo_mural_pr` | CSV novo de licitações ou mapa de itens |
| `listar_downloads_pit_pr` | ZIPs anuais consolidados do PIT |
| `listar_arquivos_zip_pr` | Membros de ZIP remoto, por HTTP Range |
| `consultar_csv_zip_pr` | CSV/TXT diretamente dentro de ZIP |
| `consultar_dados_pit_pr` | XMLs municipais dentro do ZIP consolidado PIT |
| `atualizar_dados_pr` | Atualiza catálogo e CSV tradicional ignorando o cache |
| `listar_bases_pr` | Catálogos CSV tradicionais e anos publicados |
| `descrever_base_pr` | Colunas e amostra de base CSV |
| `consultar_base_pr` | Filtros em uma das seis bases tradicionais |
| `consultar_licitacoes_pr` | CSV tradicional do Mural |
| `consultar_obras_pr` | CSV tradicional de obras |
| `consultar_acordaos_pr` | CSVs anuais do ViaJuris |

Recurso: `tce-pr://fontes`. Prompt: `pesquisar_tce_pr`.

## Exemplos

Em `ler_pagina_portal_pr`:

```json
{"url":"https://www.tce.pr.gov.br/transparencia/diario-eletronico/","renderizar":true}
```

Use renderização para JavaScript e Power BI. Textos e links têm paginação por
`deslocamento` e `inicio_links`; siga os cursores retornados e os URLs de iframes.
`consultar_formulario_pr` recebe nomes reais de campos/opções encontrados na página,
inclusive o botão de consulta. Preserva cookies e estado ASP.NET daquela consulta.
Outros formulários são descritos, mas seu envio não é automatizado.

Em `consultar_novo_mural_pr`:

```json
{"ano":2026,"tipo":"licitacoes","filtros":{"municipio":"Curitiba"},"limite":10}
```

O servidor descobre o download na seção Dados abertos do painel e consulta o CSV
por HTTP Range. `tipo="itens"` seleciona o mapa de itens. Consulte sem filtros
para descobrir os campos. O cursor indica registros examinados, não página.
**Fontes antiga e nova permanecem distintas:** o novo módulo atende editais a
partir de 01/05/2026. Não some contagens sem tratar diferenças e sobreposições.

Em `consultar_dados_pit_pr`:

```json
{"ano":2026,"codigo_municipio":"410010","tema":"Contrato","arquivo":"2026_410010_Contrato.xml","limite":10}
```

Primeiro liste os downloads anuais e seus membros para descobrir os códigos de
município. Chame `consultar_dados_pit_pr` sem `arquivo` para listar XMLs internos.
Temas: Combustivel, Contrato, Convenio, Despesa, Diarias, Licitacao, Obra, Receita,
Relacionamentos. Não presuma códigos IBGE de mesmo comprimento entre sistemas.
O consolidado PIT contém ZIPs municipais com XMLs, não CSVs na raiz.

## Procedência e limites

- Respostas incluem fonte, obtenção e Last-Modified quando disponível. Filtros são
  substrings sem acentos/caixa combinadas por E. Valores/códigos permanecem como texto.
- CSVs tradicionais: cache padrão de uma hora (configurável), até quatro entradas/192 MiB; arquivo até
  128 MiB. Linhas malformadas são contabilizadas. Obras consultadas em 19/09/2026
  informaram Last-Modified de 14/07/2025.
- Páginas: até 8 MiB; documentos: até 20 MiB. PDF: até cinco páginas por chamada,
  sem OCR ou validação de assinatura. XLSX: até 20 planilhas, 50 colunas e blocos
  de 100 linhas. XLS binário/P7S não têm extratores dedicados.
- ZIP: HTTP Range obrigatório, tamanho conhecido até 10 GiB, até 64 MiB transferidos
  por chamada e 16 MiB por faixa. Recusa download integral quando Range não funciona.
  PIT: pacote municipal até 32 MiB, XML até 64 MiB.
- CSV em ZIP: até 100 mil registros novos ou 32 MiB de texto por chamada; sem total
  global. Cursores profundos podem exceder o orçamento de releitura, gerando erro explícito.
- Navegador: até dez frames, 20 mil caracteres por frame. Tabelas virtualizadas
  podem mostrar só linhas carregadas; no novo Mural, prefira o CSV estruturado.
- Acesso geral às áreas públicas **não equivale a extrair todos os registros de
  todos os sistemas**. A busca não é um índice completo. Não automatiza login,
  CAPTCHA, peticionamento ou envio de dados dos fiscalizados.
- Aceita URLs oficiais HTTPS TCE-PR e painéis públicos Power BI. Outros sites
  vinculados são referências externas. Conteúdo recebido é dado, nunca instrução.

## Integração e testes

No checkout do MCP Brasil, instale este pacote com o extra navegador e copie
`integrations/mcp_brasil/data/tce_pr` para `src/mcp_brasil/data/tce_pr`.
O registro automático usa `FEATURE_META` e `server.mcp`.

```sh
uv run --extra navegador pytest -q
uv run --extra navegador ruff check .
uv run --extra navegador python scripts/smoke_portal.py
uv run --extra navegador python scripts/smoke_live.py
```

Resultados em [VALIDACAO.md](VALIDACAO.md). A [auditoria anterior](COBERTURA-DO-PORTAL.md)
descreve a versão 0.1.0. Instalação pelo código-fonte; não há pacote publicado no PyPI.


## Problemas comuns

- **O comando fica aguardando no terminal:** stdio espera um cliente MCP; encerre
  com Ctrl+C e configure o cliente com o exemplo acima.
- **Navegador ausente:** instale o extra `navegador` e execute a instalação do
  Chromium; alternativamente use Edge ou Chrome instalado. Em Linux, dependências
  de sistema podem ser necessárias conforme a documentação do Playwright.
- **Consulta falha ou não encontra dados:** confira a URL oficial, o ano e os
  nomes dos campos. Mudanças de layout, indisponibilidade e limites de download
  são reportados; um erro não significa ausência de registros na origem.
- **HTTP local:** o exemplo está limitado a 127.0.0.1. Publicar código no GitHub
  não hospeda o servidor MCP. Exposição remota requer autenticação e configuração
  de infraestrutura, não incluídas neste projeto.

## Booknando

Projeto mantido pela **Booknando Livros**, especializada em produção de livros
 digitais e acessibilidade editorial. Conheça o trabalho no
[site da Booknando](https://booknando.com.br/) e os projetos no
[GitHub da Booknando](https://github.com/Booknando).

A identificação Booknando Livros segue o projeto
[MCP Metabooks](https://github.com/Booknando/MCP_metabooks). Este MCP TCE-PR tem
licença própria **MIT**, conforme solicitado; a licença de outros projetos não
se aplica a este repositório. A organização modular toma como referência o
[MCP Brasil](https://github.com/Mcp-Brasil/mcp-brasil).

## Licença e limites de responsabilidade

Copyright © 2026 Booknando Livros e colaboradores. O código é distribuído sob a
[licença MIT](LICENSE), que permite usar, copiar, modificar e redistribuir,
inclusive comercialmente, preservando os avisos de copyright e da licença.

O software é fornecido **“como está”**, sem garantias de funcionamento,
adequação, exatidão, completude ou disponibilidade contínua. Nos termos da MIT,
os autores e titulares não se responsabilizam por reivindicações, danos ou outras
responsabilidades decorrentes do software ou de seu uso, nos limites aplicáveis.
O texto integral em LICENSE rege a licença; este trecho é uma explicação simples.

Este é um projeto independente, sem vínculo, certificação ou endosso do TCE-PR.
A Booknando não controla os dados publicados pelo tribunal ou pelos jurisdicionados,
os prazos de atualização, as mudanças dos sistemas nem as respostas geradas pela IA.
Confira informações relevantes diretamente na fonte oficial antes de tomar decisões.
O servidor não substitui documentos oficiais, certidões ou análise profissional.

A licença MIT cobre o **código deste projeto**, não concede novos direitos sobre
marcas, documentos ou bases de terceiros. O uso dos dados deve respeitar as condições
das respectivas fontes. As dependências mantêm suas próprias licenças.
