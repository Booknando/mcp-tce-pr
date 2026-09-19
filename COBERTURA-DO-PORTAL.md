# Auditoria de cobertura do portal TCE-PR

Data: 19/09/2026. Versão auditada: 0.1.0.

> **Documento histórico.** A versão 0.2.0, posterior a esta auditoria, adiciona
> navegação geral, renderização, documentos, consulta processual, PIT e acesso
> separado ao novo Mural. Consulte README.md e VALIDACAO.md para o estado atual.

## Conclusão

**Não foi utilizado tudo o que o portal fornece.** A versão criada é uma primeira
integração com seis bases CSV: licitações, obras, acompanhamentos, responsáveis
técnicos, bens patrimoniais e acórdãos. As seis ferramentas MCP são interfaces
para essas bases; não representam seis sistemas completos do tribunal.

Os 14 testes e as consultas reais anteriores comprovam funcionamento desse recorte,
não completude do portal. O número de 48 arquivos refere-se aos catálogos integrados,
não a um inventário de todos os dados do TCE-PR.

## Lacuna prioritária: novo Mural de Licitações

O tribunal informa que os editais com data a partir de **01/05/2026** pertencem ao
novo módulo. O ambiente anterior permanece para editais até **30/04/2026**, com
transição durante 2026. O portal oferece um painel separado em Power BI.
[Publicação oficial de 12/05/2026](https://www.tce.pr.gov.br/noticias/novo-modulo-do-sim-am-adequa-envio-de-dados-de-licitacoes-a-lei-14-133-21.htm).

O MCP usa `2026_mural_de_licitacoes_base_de_dados.csv` do catálogo tradicional.
**Não foi demonstrado que esse CSV contém os registros do novo módulo.** Portanto,
consultar o arquivo de 2026 não garante cobertura integral das licitações desse ano.
Também não se pode afirmar, sem comparar os registros, que ele exclui todos os
editais posteriores ao corte. Essa verificação ficou pendente.

## Comparação por área

| Área / fonte | Cobertura na versão 0.1.0 | O que falta |
|---|---|---|
| [Dados abertos tradicionais](https://servicos.tce.pr.gov.br/servicos/srv_dados_abertos.aspx) | CSVs de licitações e quatro bases de obras | Expor dicionários XLSX, modelo de relacionamento e regras como recursos consultáveis |
| [ViaJuris — bases anuais](https://viajuris.tce.pr.gov.br/DadosAbertos/DadosAbertos/BaseDados) | CSVs de acórdãos; ementas e links PDF | Pesquisa online com todos os filtros, leitura dos PDFs e validação de cobertura dos demais tipos de decisão |
| [Novo Mural](https://www.tce.pr.gov.br/fiscalizado/mural-de-licitacoes-cadastro-de-licitacoes-municipais/) | Não integrado como fonte distinta | Validar exportação/consulta e distinguir os períodos do mural |
| [PIT — dados por município](https://pit.tce.pr.gov.br/Dados/DadosConsulta/Consulta) | Não integrado | Download por município/ano; contratos, despesas e outros temas; relacionamentos |
| [PIT — consolidado](https://pit.tce.pr.gov.br/Dados/DadosConsulta/Consolidado) | Não integrado | Importar arquivos anuais de todos os municípios e seus vínculos |
| [Consulta processual pública](https://servicos.tce.pr.gov.br/servicos/srv_consultaprocesso.aspx) | Não integrada | Consulta por protocolo e por ofício/entidade; tramitação. A página pública existe, não deve ser confundida com acesso autenticado ao e-Contas |
| [Diário Eletrônico](https://www.tce.pr.gov.br/transparencia/diario-eletronico/) | Não integrado | Pesquisa por número, texto e período; recuperação de publicações PDF/P7S |
| [Atos normativos](https://www.tce.pr.gov.br/fiscalizado/atos-normativos-do-tce/consulta-de-atos/) | Não integrados | Resoluções, instruções, notas técnicas, portarias e provimentos |
| [Súmulas](https://www.tce.pr.gov.br/fiscalizado/decisoes-do-tribunal/sumulas/) e [prejulgados](https://www.tce.pr.gov.br/fiscalizado/decisoes-do-tribunal/prejulgados/) | Sem conectores específicos | Busca por número, palavras, assunto e datas; texto e anexos |
| [Demais coleções de jurisprudência](https://www.tce.pr.gov.br/cidadao/) | Cobertura não demonstrada pelos CSVs de acórdãos | Decisões monocráticas, antigas, consultas, uniformização, incidentes, pesquisas prontas e boletins |
| [Multas e sanções](https://servicos.tce.pr.gov.br/servicos/srv_relatorio_multas_sancoes.aspx) | Não integradas | Formulário por processo, ato, relator e tipo de sanção |
| [Inadimplentes](https://www.tce.pr.gov.br/transparencia-do-tce-pr/processos-e-decisoes/cadastro-de-inadimplentes.htm) | Não integrado | Consulta de débitos e pendências; distinguir de condenações e contas irregulares |
| [Certidões](https://www.tce.pr.gov.br/para-o-fiscalizado/servicos/certidoes/) | Não integradas | Mapear separadamente consulta, validação e eventual emissão |
| [Transferências voluntárias](https://www.tce.pr.gov.br/para-o-fiscalizado/servicos/transferencias-voluntarias.htm) | Não integradas | Consulta pública e relação com convênios; diferenciar módulos restritos de envio |
| [Serviços do fiscalizado](https://www.tce.pr.gov.br/para-o-fiscalizado/servicos/consulta-processual.htm) | Fora do conector atual | Cadastro de entidades, agenda de obrigações, restrições, Atoteca e histórico de cumprimento de decisões |
| [Licitações do próprio tribunal](https://www.tce.pr.gov.br/transparencia-do-tce-pr/licitacoes-e-contratos/licitacoes.htm) | Não integradas | PNCP do TCE a partir de 2023 e SALC até 2022; não são o Mural municipal |
| [Despesas do próprio tribunal](https://www.tce.pr.gov.br/transparencia-do-tce-pr/despesa/despesa-detalhada.htm) | Não integradas | Relatórios de despesas e empenhos; fontes distintas até 2023 e a partir de 2024 |
| [Remuneração](https://www.tce.pr.gov.br/transparencia-do-tce-pr/pessoal/remuneracao.htm) | Não integrada | Consulta por filtros e nome; separar outros dados de pessoal |
| [Transparência institucional](https://www.tce.pr.gov.br/transparencia/) | Não integrada | Sessões, contratos, patrimônio, receitas, balanços, relatórios de atividade, diárias e demais coleções do menu |
| [Transparência municipal](https://www.tce.pr.gov.br/transparencia/municipios/) | Parcial apenas pelo recorte CSV municipal | PROGOV, PROLEGIS, gestão fiscal, indicadores e gestão em foco |
| [Transparência estadual](https://www.tce.pr.gov.br/transparencia/transparencia-do-estado.htm) | Não integrada | Dados gerais do Executivo e gestão fiscal estadual |
| [Painéis da página inicial](https://www.tce.pr.gov.br/) | Não integrados | Emendas/Pix, educação, saúde, PPA, tributação, eventos, ODS, segurança pública e fiscalização |
| Notícias, biblioteca, manuais, cursos e ouvidoria | Fora da versão inicial | Descoberta de conteúdo público; inscrições e manifestações são operações diferentes de leitura |

## Fonte adicional concreta: PIT consolidado

A página de download consolidado apresenta anos de 2013 a 2026 e explica que
os pacotes abrangem todos os municípios, com atualização semanal e arquivo de
relacionamentos. O link de 2026 resolve para
[2026_PIT_TodosArquivos.zip](https://pit.tce.pr.gov.br/Arquivos/2026_PIT_TodosArquivos.zip).

Foi identificado o link; **o conteúdo e o tamanho do ZIP não foram validados nesta
auditoria**. Antes de integrá-lo, será necessário inspecionar o esquema, os arquivos
internos, os identificadores e a atualização. As consultas e os downloads do PIT
merecem um cliente próprio, separado do leitor dos CSVs tradicionais.

## Ordem sugerida para ampliar

1. Validar o novo Mural e tornar explícita a cobertura temporal das licitações.
2. Integrar PIT: entidades/municípios, receitas, despesas, contratos, convênios,
   combustíveis, downloads e vínculos entre temas.
3. Acrescentar consulta processual pública, Diário Eletrônico e atos normativos.
4. Ampliar jurisprudência: precedentes, demais decisões e leitura de PDFs.
5. Acrescentar sanções, pendências, contas irregulares, certidões e sessões.
6. Integrar transparência do próprio tribunal e demais painéis conforme a
   disponibilidade de fontes públicas estáveis.

Para cada conector, confirmar esquema/paginação, referência temporal, procedência
e ao menos uma consulta real. Um link ou formulário visível não comprova que exista
uma API documentada ou exportação automatizável.

## Método e limites

Foram percorridas as páginas inicial, Cidadão, Transparência, serviços do fiscalizado,
links do PIT e páginas especializadas listadas acima, comparando-as com os módulos
`constants.py`, `tools.py` e o escopo documentado do MCP. O mapa do site foi aberto,
mas sua árvore depende de carregamento dinâmico.

A leitura foi feita pelas páginas e links acessíveis à ferramenta de navegação web.
A tentativa adicional de abrir o navegador interativo falhou por timeout do ambiente.
O conteúdo interno do Power BI não pôde ser inspecionado; sua finalidade e separação
temporal foram confirmadas no portal e nas publicações oficiais. A página de sessões
também não foi carregada pela ferramenta, ficando identificada pelo menu oficial.

Não foram submetidos todos os formulários, verificadas todas as combinações de
filtros, acessados sistemas restritos ou inventariados todos os documentos individuais.
Esta é uma auditoria das áreas e lacunas encontradas, não uma alegação de varredura
integral do site. Não se atribui um percentual de cobertura sem um universo definido.

Nesta revisão foi atualizada a documentação; **nenhuma ferramenta nova foi implementada**.
