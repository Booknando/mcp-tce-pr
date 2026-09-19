# Validação — 19/09/2026

## Versão 0.3.0

40 testes passaram em Windows/Python 3.12.13; análise Ruff aprovada.
Novos testes confirmam atualização forçada pela ferramenta MCP, substituição
do conteúdo antigo no cache, expiração, cache desativado, configuração inválida
e erro explícito quando a atualização falha. O protocolo stdio foi exercitado.
O workflow Linux/Python 3.11–3.13 está preparado; não foi executado localmente.
Os testes da atualização usam respostas HTTP simuladas, com conteúdo alterado
entre chamadas. As verificações reais de cobertura abaixo são da versão 0.2.0.

## Versão 0.2.0 — fontes reais

Ambiente: Windows, Python 3.12.13, FastMCP 3.4.7, Playwright 1.63.0.
Dependências fixadas em uv.lock. Navegador: Edge headless, perfil isolado.
A CDN do Chromium apresentou timeout; a alternativa Edge foi validada.

## Fontes reais

- Leitura HTTP das **22 áreas** cadastradas, sem falhas na rodada final.
- Diário Eletrônico e atos normativos: renderização retornou conteúdo/links adicionais.
- Mapa do site: página lida; não se afirma expansão integral de sua árvore dinâmica.
- Novo Mural: painel Power BI e seção Dados abertos acessados; downloads CSV/JSON/XML
  globais e por município, além de layouts, encontrados no DOM renderizado.
- CSV novo `licitacao_municipal_2026.csv`: um registro lido por Range, com **72 campos**,
  transferindo cerca de **8,4 KB**. CSV de 31.392.999 bytes dentro de ZIP de 4.523.727 bytes.
- Consulta processual `196886/26`: resposta oficial recebida em URL contendo
  `processoMaster=19688626`, com links para continuidade da consulta.
- Documento ViaJuris: extraídos 5.619 caracteres das primeiras três páginas de
  documento com quatro páginas. O parser reportou estrutura irregular; a leitura
  não certifica assinatura ou integridade jurídica.

## PIT

ZIP anual 2026: **741.379.999 bytes**, **3.591 ZIPs internos**.
Inventário obtido com **253.008 bytes** transferidos. Os primeiros XMLs dos nove
temas do município `410010` foram abertos e consultados:

| Tema | XML | Registros |
|---|---|---:|
| Combustivel | Combustivel | 1.243 |
| Contrato | Contrato | 133 |
| Convenio | Convenio | 0 |
| Despesa | Empenho | 3.051 |
| Diarias | Diarias | 172 |
| Licitacao | Licitacao | 121 |
| Obra | Intervencao | 1 |
| Receita | ReceitasConsolidado | 553 |
| Relacionamentos | ContratoXConvenio | 0 |

Zero significa arquivo vazio nessa amostra, não ausência universal do tema.
Não foram testados todos os XMLs, municípios, filtros ou anos.

## Testes

**33 testes passaram**; `ruff check .` passou sem problemas. A suíte inclui
inicialização de subprocesso stdio e descoberta das ferramentas por cliente MCP.
O mapa de itens do novo Mural também retornou um registro real, com 45 campos,
transferindo 8.386 bytes. A ferramenta dedicada ao novo Mural foi exercitada
de ponta a ponta: descoberta no painel, seleção do ZIP e leitura do CSV.

A suíte cobre CSV, codificação, paginação, cache, erros HTTP, redirects, limites,
formulários ASP.NET, busca com escopo, extração PDF/XLSX, ZIP remoto com Range,
recusa de download integral, cursor, ZIPs aninhados, XML e bloqueio de DTD/entidades,
MCP em memória e stdio.

As seis bases CSV tradicionais foram consultadas na validação da 0.1.0. Seus
resultados permanecem um recorte específico, não uma medida de cobertura de todo
o portal. A versão 0.2.0 amplia as formas de acesso sem alegar extração exaustiva
de todos os painéis, autenticação ou execução de operações transacionais.
