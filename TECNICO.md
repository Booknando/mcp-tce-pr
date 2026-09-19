# Guia técnico — MCP TCE-PR

[Voltar ao guia de instalação](README.md)

Documento para equipes de TI e desenvolvedores. Versão 0.3.0, Python 3.11+, FastMCP.
A organização modular toma como referência o [MCP Brasil](https://github.com/Mcp-Brasil/mcp-brasil).

## Instalação para desenvolvimento

```sh
git clone https://github.com/Booknando/mcp-tce-pr.git
cd mcp-tce-pr
uv sync --locked --extra navegador
uv run --extra navegador playwright install chromium
```

O transporte padrão é **stdio**. A renderização tenta Chromium e depois Edge/Chrome
instalados, sempre com perfil temporário sem cookies e credenciais do usuário.
Se Edge/Chrome já estiver disponível, a instalação do Chromium pode ser dispensada.
`MCP_TCE_BROWSER_CHANNEL=msedge` ou `chrome` define a primeira opção.

## Transporte HTTP local

HTTP local opcional, sem autenticação:

```sh
uv run --extra navegador python -c "from mcp_tce_pr.server import mcp; mcp.run(transport='http', host='127.0.0.1', port=8000)"
```

O exemplo escuta apenas em 127.0.0.1 e não oferece autenticação. Hospedagem
remota exige infraestrutura, controle de acesso e configuração próprios.
Publicar este repositório não hospeda um servidor acessível por URL.

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


## macOS, Linux e outros clientes

Instale uv conforme sua [documentação oficial](https://docs.astral.sh/uv/getting-started/installation/),
abra um terminal na pasta do projeto e execute os comandos de instalação acima.
Em Linux, o Playwright pode exigir bibliotecas do sistema; a equipe de TI deve
consultar a [documentação de navegadores](https://playwright.dev/python/docs/browsers).
A validação local registrada neste projeto foi feita em Windows.

O servidor usa stdio por padrão. Configure o cliente para executar o Python do
ambiente virtual, com os argumentos `-m mcp_tce_pr.server`. No Windows o executável
fica em `.venv/Scripts/python.exe`; no macOS/Linux, em `.venv/bin/python`.
Use caminhos absolutos. O cliente inicia o servidor; não é necessário manter um
terminal executando o MCP. Formatos de configuração variam entre clientes.

Exemplo genérico para clientes que aceitam `mcpServers`:

```json
{
  "mcpServers": {
    "tce-pr": {
      "command": "/caminho/absoluto/mcp-tce-pr/.venv/bin/python",
      "args": ["-m", "mcp_tce_pr.server"],
      "env": {"MCP_TCE_CACHE_SECONDS": "3600"}
    }
  }
}
```

O procedimento do README configura MCP local no Claude Desktop. Ele não fornece
uma extensão MCPB nem integração específica validada para Cowork. Outros clientes
precisam suportar execução de servidores locais; uma tela que solicita somente
URL de conector remoto não aceita o caminho deste programa.

## Arquitetura

- `client.py`, `schemas.py`, `tools.py`: catálogos e CSVs tradicionais, filtros e cache.
- `portal.py`, `portal_tools.py`, `render.py`: navegação pública, formulários e JavaScript.
- `archives.py`, `pit.py`: ZIPs remotos, CSV e pacotes XML municipais.
- `documents.py`: extração de documentos públicos.
- `server.py`, `resources.py`, `prompts.py`: registro MCP, recurso de fontes e prompt.
- `integrations/`: adaptador para MCP Brasil.

A ferramenta de atualização renova apenas o cache do processo que a recebeu.
Ela não escreve nas fontes oficiais. Não existe banco local persistente nem tarefa
agendada. As ferramentas não implementam login, CAPTCHA ou envio de informações
ao tribunal. Conteúdo externo deve ser tratado como dado, nunca como instrução.

## Diagnóstico

Execute na pasta do projeto:

```sh
uv run --extra navegador python -c "from mcp_tce_pr.server import mcp; print('Servidor carregado com sucesso')"
uv run --extra navegador pytest -q
uv run --extra navegador ruff check .
```

Os scripts `smoke_live.py` e `smoke_portal.py` fazem consultas reais e dependem da
rede e da disponibilidade das fontes. Os testes automatizados não comprovam cobertura
integral do portal. Consulte [VALIDACAO.md](VALIDACAO.md) para os resultados e limites.
