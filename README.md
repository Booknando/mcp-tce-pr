# MCP TCE-PR

**Consulte informações públicas do Tribunal de Contas do Estado do Paraná na conversa com seu assistente de inteligência artificial.**

Uma iniciativa da **[Booknando Livros](https://booknando.com.br/)**. Projeto independente, sem vínculo oficial com o TCE-PR.

Este guia foi escrito para quem trabalha em uma prefeitura, câmara municipal ou outro órgão e quer instalar a ferramenta sem precisar saber programar. O passo a passo usa **Windows e Claude Desktop**.

> O programa consulta dados públicos. Não envia prestações de contas, não protocola documentos e não altera informações no TCE-PR. Confira os resultados nas fontes oficiais antes de usá-los em decisões ou documentos de trabalho.

## Comece por aqui

- [O que você pode consultar](#o-que-você-pode-consultar)
- [O que precisa ter](#o-que-precisa-ter)
- [Instalação passo a passo](#instalação-passo-a-passo)
- [Como usar no dia a dia](#como-usar-no-dia-a-dia)
- [Os dados são atualizados?](#os-dados-são-atualizados)
- [Se algo não funcionar](#se-algo-não-funcionar)
- [Limitações](#limitações-que-você-precisa-conhecer)
- **Para a equipe de TI:** [guia técnico, ferramentas e configurações](TECNICO.md)

## O que você pode consultar

| Sua necessidade | Como o MCP pode ajudar |
| --- | --- |
| Consultar obras do município | Localizar registros nas bases públicas de obras |
| Pesquisar licitações | Consultar o Mural tradicional e a nova fonte de licitações |
| Encontrar decisões do tribunal | Pesquisar acórdãos publicados no ViaJuris |
| Consultar um processo | Acessar a consulta pública pelo número do protocolo |
| Ler informações do portal | Abrir páginas, seguir links e ler documentos compatíveis |
| Explorar dados municipais | Consultar as bases do Portal de Informações para Todos, o PIT |

**MCP é a conexão entre o assistente e as fontes de informação.** Você escreve uma pergunta; o assistente usa este programa para consultar o TCE-PR e recebe os resultados. Depois, pode organizar os dados e explicar o que encontrou.

O programa roda no seu computador. Não é necessário criar conta no TCE-PR para as fontes públicas atendidas, nem baixar previamente todas as bases. As consultas têm limites e não abrangem automaticamente todos os registros de cada sistema.

## O que precisa ter

- Um computador com **Windows 10 ou 11** e acesso à internet.
- O **[Claude Desktop](https://claude.ai/download)** instalado e uma conta que permita usar as ferramentas locais do aplicativo. O guia não se aplica à versão aberta apenas no navegador.
- Permissão para instalar programas. Se o equipamento for gerenciado pelo município, encaminhe este guia à equipe de TI quando necessário.

O código deste MCP é gratuito sob licença MIT. O aplicativo de IA pode ter seus próprios planos, custos e limites. Use um serviço autorizado pelo seu órgão; consultas e resultados enviados ao assistente seguem as regras de privacidade desse serviço.

**Você não precisa instalar Git, ter conta no GitHub ou saber Python.** O roteiro abaixo instala os componentes necessários.

## Instalação passo a passo

Faça uma etapa por vez. Nos blocos de comandos, copie somente o conteúdo do bloco, cole no PowerShell e pressione **Enter**. Espere o comando terminar antes de continuar.

### Passo 1 — Baixar e extrair o projeto

1. [Clique aqui para baixar o projeto em ZIP](https://github.com/Booknando/mcp-tce-pr/archive/refs/heads/main.zip). Também pode usar o botão verde **Code → Download ZIP** nesta página.
2. Abra a pasta **Downloads** do Windows.
3. Clique com o botão direito no ZIP baixado e escolha **Extrair Tudo**.
4. Abra a pasta extraída até encontrar **README.md**, **pyproject.toml** e **uv.lock**. Essa é a pasta do projeto. Às vezes, existe uma pasta dentro de outra com o mesmo nome.
5. Mova essa pasta para um local onde pretende mantê-la, por exemplo **Documentos**. Pode renomeá-la para **mcp-tce-pr**.

**Não execute dentro do ZIP e não mova a pasta depois da instalação.** A conexão usará o endereço dessa pasta. Se mudar o local, repita a instalação e a configuração no novo endereço.

### Passo 2 — Instalar o auxiliar de instalação

Vamos instalar o **uv**, um programa que prepara o ambiente necessário para o MCP.

1. Abra o menu **Iniciar**, digite **PowerShell** e abra o aplicativo.
2. Execute:

```powershell
winget install --id=astral-sh.uv -e
```

3. Siga as mensagens do instalador. Se já estiver instalado, prossiga.
4. **Feche o PowerShell e abra-o novamente.**
5. Confira:

```powershell
uv --version
```

**Resultado esperado:** uma linha começando com `uv`, seguida de um número de versão. Se aparecer “não reconhecido”, consulte [Se algo não funcionar](#se-algo-não-funcionar).

Esse método segue a [documentação oficial do uv](https://docs.astral.sh/uv/getting-started/installation/). Se faltar `winget` ou o computador bloquear instalações, peça à TI para instalar o uv por um dos métodos oficiais.

### Passo 3 — Abrir o PowerShell na pasta certa

1. No Explorador de Arquivos, abra a pasta que contém **pyproject.toml**.
2. Clique na **barra de endereço** no alto da janela, digite `powershell` e pressione **Enter**.
3. Na janela que abrir, execute:

```powershell
Test-Path .\pyproject.toml
```

**Resultado esperado:** `True`. Se aparecer `False`, você está na pasta errada. Localize a pasta que contém o arquivo antes de continuar.

### Passo 4 — Instalar os componentes do MCP

No PowerShell aberto na pasta do projeto, execute os comandos **um de cada vez**:

```powershell
uv python install 3.12
```

```powershell
uv sync --locked --python 3.12 --extra navegador
```

```powershell
uv run --extra navegador playwright install chromium
```

O primeiro instala o Python necessário. O segundo instala o MCP e suas dependências. O terceiro instala o navegador usado pelo programa para ler páginas que carregam informações dinamicamente. O download pode levar alguns minutos.

Para conferir, execute:

```powershell
uv run --extra navegador python -c "from mcp_tce_pr.server import mcp; print('Instalação concluída')"
```

**Resultado esperado:** `Instalação concluída`, sem erro. Essa conferência verifica o carregamento do programa; a consulta ao portal será testada no passo 7.

### Passo 5 — Gerar a configuração do seu computador

Ainda no mesmo PowerShell, copie e execute **todo este bloco**:

```powershell
$pythonMcp = (Resolve-Path .\.venv\Scripts\python.exe).Path
@{
  mcpServers = @{
    'tce-pr' = @{
      command = $pythonMcp
      args = @('-m', 'mcp_tce_pr.server')
    }
  }
} | ConvertTo-Json -Depth 5
```

O comando mostra um texto de configuração com o endereço correto da instalação. Ele **não altera as configurações do Claude**.

Copie o resultado inteiro, da primeira `{` até a última `}`. Ele terá uma estrutura parecida com esta, mas com seu usuário e a pasta escolhida:

```json
{
  "mcpServers": {
    "tce-pr": {
      "command": "C:\\Users\\SEU_USUARIO\\Documents\\mcp-tce-pr\\.venv\\Scripts\\python.exe",
      "args": ["-m", "mcp_tce_pr.server"]
    }
  }
}
```

**Use o resultado gerado no seu PowerShell**, não o caminho fictício acima. As barras duplas no endereço são normais nesse formato.

### Passo 6 — Conectar ao Claude Desktop

1. Abra o **Claude Desktop**.
2. Entre em **Settings → Developer → Edit Config** — em português, procure **Configurações → Desenvolvedor → Editar configuração**.
3. Abra **claude_desktop_config.json** em um editor de texto, como o Bloco de Notas. No Windows, ele costuma ficar em `%APPDATA%\Claude`.
4. Faça uma cópia do arquivo como backup e encerre completamente o Claude, inclusive pelo ícone ao lado do relógio, se houver.
5. Se o arquivo estiver vazio ou contiver apenas `{}`, cole **todo o resultado do passo 5**.
6. Salve sem mudar o nome do arquivo ou acrescentar `.txt`.
7. Abra o Claude Desktop novamente.

**Já existem outras configurações ou conexões no arquivo?** Preserve-as. Acrescente somente a entrada `"tce-pr": { ... }` dentro de `"mcpServers"`, separada das outras por vírgula. Se ainda não existir `mcpServers`, acrescente esse bloco preservando as demais opções. Se já existir `tce-pr`, substitua apenas essa entrada. Peça ajuda à TI se não estiver seguro ao editar: uma vírgula fora do lugar pode impedir o carregamento.

Referência: [guia oficial de conexão de servidores MCP locais](https://modelcontextprotocol.io/docs/develop/connect-local-servers). Os menus podem variar entre versões do aplicativo.

### Passo 7 — Fazer a primeira consulta

Abra uma nova conversa no Claude Desktop e escreva:

> Use o MCP tce-pr para listar as áreas públicas disponíveis no portal do TCE-PR.

Se o aplicativo solicitar permissão para usar a ferramenta, confira o pedido e autorize a consulta.

**Resultado esperado:** o assistente utiliza `listar_areas_portal_pr` e apresenta as áreas cadastradas. Isso confirma a conexão com o MCP. Em seguida, teste o acesso à internet:

> Use o MCP tce-pr para ler a página https://www.tce.pr.gov.br/ e mostrar o título e alguns links encontrados.

Essa segunda consulta deve retornar informações obtidas do portal. Uma resposta genérica, sem uso das ferramentas, não confirma que a instalação funcionou.

Depois de conectado, **não precisa deixar o PowerShell aberto**. O cliente inicia o MCP quando necessário. Mantenha a pasta do projeto no lugar.

## Como usar no dia a dia

Escreva o município, o período e o assunto desejado. Não precisa decorar os nomes das ferramentas.

| O que deseja fazer | Exemplo de pedido |
| --- | --- |
| Ver obras | “Consulte as obras de Curitiba. Mostre a fonte e a data de obtenção dos dados.” |
| Pesquisar licitações | “Pesquise licitações de merenda escolar de Londrina na base de 2026. Confira as fontes tradicional e nova e explique a cobertura de cada uma.” |
| Consultar processo | “Consulte o processo de protocolo [número/ano] no TCE-PR e mostre os links oficiais encontrados.” |
| Encontrar decisões | “Pesquise acórdãos da base de 2026 sobre transporte escolar e apresente as ementas e os links disponíveis.” |
| Conferir informações recentes | “Atualize a base de obras antes de consultar meu município e informe quando os dados foram obtidos.” |

Substitua nomes, anos e protocolo pelos que precisa pesquisar. Para consultas extensas, peça ao assistente que continue pelos próximos resultados e informe o que ainda não foi consultado.

## Os dados são atualizados?

**Sim. O programa consulta as fontes oficiais durante o uso.**

- Páginas, documentos, PIT e novo Mural são buscados a cada consulta.
- Algumas bases tradicionais usam uma cópia temporária para acelerar as respostas. Por padrão, ela vale por uma hora; depois disso, a próxima consulta busca a fonte novamente.
- Você pode pedir uma atualização imediata das bases tradicionais, como no exemplo de obras acima.

**Buscar novamente não significa que o TCE-PR publicou dados novos.** A data da consulta é diferente da data de atualização dos registros. Se a fonte estiver desatualizada, o MCP não consegue corrigir isso. Sem consultas, o programa não fica monitorando nem baixando dados em segundo plano.

## Se algo não funcionar

| O que apareceu | O que fazer |
| --- | --- |
| `winget` ou `uv` não é reconhecido | Para uv, feche e reabra o PowerShell após a instalação. Se continuar, ou se faltar winget, encaminhe o passo 2 à TI. |
| O teste da pasta retornou `False` | Abra a pasta extraída que contém `pyproject.toml`, não o ZIP nem a pasta acima dela. |
| O download falhou ou a rede bloqueou | Guarde a mensagem e peça à TI para verificar conexão e permissões de download. Não desative as proteções do computador. |
| A instalação do Chromium falhou | O programa também tenta Edge ou Chrome instalado. Peça à TI para verificar essa alternativa no guia técnico; a leitura de páginas dinâmicas ainda precisa ser testada. |
| O MCP não aparece no Claude | Confira se está no aplicativo Desktop, se o arquivo foi salvo como `.json` e se usou a configuração do passo 5. Encerre e reabra o Claude completamente. |
| Parou depois que a pasta foi movida | Repita os passos 3 a 6 no local definitivo. |
| A consulta demorou ou retornou erro | A fonte pode estar indisponível ou a consulta ultrapassar um limite. Tente um município ou período menor e confira o portal oficial. |
| Não foram encontrados registros | Confira município, ano e fonte. Isso não comprova que não existam registros em outros sistemas do tribunal. |

Para pedir ajuda, envie à TI o passo em que parou e a mensagem completa do erro. Também pode [registrar um problema no projeto](https://github.com/Booknando/mcp-tce-pr/issues), sem incluir senhas ou informações pessoais e sigilosas.

## Como atualizar o programa

As melhorias do programa são distribuídas pelo GitHub. Isso é diferente da atualização dos dados consultados.

1. Encerre o Claude Desktop completamente.
2. Baixe o ZIP novamente pelo link do passo 1.
3. Extraia em uma **nova pasta**, mantendo a instalação anterior até conferir a nova.
4. Repita os passos 3 a 5 na nova pasta.
5. No arquivo do Claude, substitua a entrada `tce-pr` pela nova configuração. Preserve as outras entradas.
6. Reabra o Claude e faça os testes do passo 7.

Não copie a pasta `.venv` da instalação antiga: ela será criada novamente. O programa não se atualiza sozinho.

## Limitações que você precisa conhecer

- Acesso às áreas públicas não garante leitura completa de todos os sistemas, tabelas ou documentos do portal.
- Não acessa áreas com login, não resolve CAPTCHA e não realiza peticionamento ou envio de dados ao tribunal.
- Pesquisas e documentos grandes podem precisar de várias consultas. PDFs digitalizados como imagem não têm reconhecimento de texto nesta versão.
- Mudanças no portal, falhas de rede e arquivos incompatíveis podem interromper consultas.
- As fontes do Mural tradicional e do novo Mural têm coberturas diferentes. Não some resultados sem conferir repetições e diferenças.
- A IA pode interpretar informações incorretamente. Confira os links oficiais e os dados originais.

## Para a equipe de TI

O [guia técnico](TECNICO.md) reúne configurações de cache, outros sistemas operacionais, transporte HTTP, catálogo das 19 ferramentas, limites de leitura, integração com MCP Brasil e comandos de teste.

O servidor foi validado localmente em Windows com Python 3.12. Os testes do protocolo MCP passaram; a configuração para Claude Desktop segue o guia oficial, mas não representa validação de todas as versões do aplicativo. Veja [VALIDACAO.md](VALIDACAO.md).

## Sobre a Booknando

A **[Booknando Livros](https://booknando.com.br/)** oferece serviços e tecnologia para editoras, com atuação em livros digitais, EPUB, acessibilidade editorial e soluções para melhorar os processos de produção.

Este projeto disponibiliza uma conexão aberta entre assistentes de IA e informações públicas do TCE-PR. Conheça nossos serviços e entre em contato pelo [site da Booknando](https://booknando.com.br/).

## Licença e aviso de responsabilidade

Copyright © 2026 Booknando Livros e colaboradores. Código aberto sob a **[licença MIT](LICENSE)**: você pode usar, copiar, modificar e redistribuir o software, inclusive comercialmente, preservando os avisos da licença.

**O uso é por conta e responsabilidade de cada usuário.** O software é fornecido no estado em que se encontra, sem garantias de exatidão, completude, funcionamento contínuo ou adequação a uma finalidade específica, nos termos da MIT.

Cabe ao usuário revisar os resultados, conferir as fontes oficiais, seguir as regras do seu órgão e verificar quais informações compartilha com os serviços de IA. O MCP não substitui documentos oficiais, certidões, análise profissional ou os sistemas de prestação de contas.

Na máxima extensão permitida pela legislação aplicável, a Booknando, os autores, os titulares dos direitos e os colaboradores não se responsabilizam por danos ou prejuízos decorrentes do uso ou da impossibilidade de uso do software. A disponibilização do projeto não inclui compromisso de suporte, manutenção ou disponibilidade contínua; serviços contratados separadamente seguem seus próprios termos.

Este projeto não tem vínculo, certificação ou endosso do TCE-PR. A Booknando não controla as informações publicadas pelo tribunal e pelos jurisdicionados, seus prazos de atualização nem as respostas geradas pela IA. A licença MIT cobre o código deste projeto; dados, documentos, marcas e dependências de terceiros mantêm suas condições próprias.

Este aviso complementa a licença, sem alterar suas permissões nem afastar responsabilidades que não possam ser excluídas. Consulte o texto integral em [LICENSE](LICENSE).
