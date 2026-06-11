# Early detection de ransomware

# Ransomware Temporal API Dataset Generator

Artefato de apoio à pesquisa de mestrado voltado à geração de datasets temporais a partir de logs de análise dinâmica de programas, com foco em chamadas de API e comportamento de processos.

O objetivo do artefato é transformar arquivos JSON de análise dinâmica em dois datasets estruturados:

1. **Dataset baseado em processos**, contendo informações agregadas de cada processo observado.
2. **Dataset baseado em chamadas de API**, contendo cada chamada de API realizada, com seu respectivo tempo relativo.

Esses datasets servem como base para análises posteriores envolvendo classificação de API calls, correlação temporal, comportamento de processos e identificação de padrões relacionados a ransomware.

---

## 1. Visão geral do artefato

Este artefato processa arquivos JSON contendo informações comportamentais de execuções de binários analisados em ambiente controlado.

A partir desses arquivos, o script extrai:

* identificador da execução;
* nome do binário analisado;
* score da análise;
* processos observados;
* PID e Parent PID;
* nome do processo;
* linha de comando;
* chamadas de API;
* tempo absoluto de cada chamada;
* tempo relativo em milissegundos;
* duração de cada processo;
* quantidade de chamadas de API por processo.

O script gera dois arquivos CSV finais:

```text
dataset_processos.csv
dataset_chamadas.csv
```

Esses arquivos podem ser usados em etapas posteriores da pesquisa, como:

* classificação de API calls;
* análise temporal;
* agrupamento de chamadas por categoria;
* correlação entre processos e chamadas;
* identificação de padrões comportamentais;
* geração de relatórios e visualizações.

---

## 2. Relação com a pesquisa de mestrado

Este artefato está inserido em uma pesquisa sobre análise comportamental de ransomware baseada em chamadas de API.

Enquanto trabalhos relacionados utilizam sequências de API calls para detectar ou classificar ransomwares, este artefato tem como foco inicial organizar os dados em uma estrutura temporal, permitindo responder perguntas como:

* Quais processos foram criados durante a execução?
* Quais APIs foram chamadas por cada processo?
* Em que momento relativo cada chamada ocorreu?
* Qual processo iniciou primeiro?
* Quanto tempo cada processo permaneceu ativo?
* Quais processos concentraram mais chamadas de API?
* Como relacionar chamadas individuais com o comportamento agregado do processo?

A proposta futura é utilizar esses datasets para classificar chamadas de API em categorias comportamentais, como:

* Arquivo;
* Registro;
* Processo;
* Memória;
* Rede;
* Criptografia;
* Evasão;
* Sistema.

---

## 3. Estrutura esperada do repositório

A estrutura recomendada para o repositório é:

```text
ransomware-temporal-api-dataset/
│
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
│
├── src/
│   └── dataser-temporal.py
│
├── data/
│   ├── raw/
│   │   └── exemplo.json
│   ├── processed/
│   │   ├── dataset_processos.csv
│   │   └── dataset_chamadas.csv
│   └── README.md
│
├── docs/
│   ├── metodologia.md
│   ├── esquema_dos_datasets.md
│   ├── avaliacao_artefato.md
│   └── limitacoes.md
│
├── results/
│   ├── logs/
│   │   └── geracao_datasets_temporais.log
│   └── exemplos/
│
├── artifact/
│   ├── ARTIFACT.md
│   ├── INSTALL.md
│   ├── REPRODUCIBILITY.md
│   └── CHECKLIST.md
│
└── tests/
    └── README.md
```

---

## 4. Requisitos

O script foi desenvolvido em Python e utiliza apenas bibliotecas padrão da linguagem.

### Bibliotecas utilizadas

O código utiliza:

```python
glob
json
csv
os
logging
pathlib
```

Como todas essas bibliotecas fazem parte da biblioteca padrão do Python, não é necessário instalar dependências externas para executar a versão atual do script.

### Ambiente utilizado no desenvolvimento

O script foi executado utilizando:

* Anaconda;
* PyCharm;
* Python 3.10 ou superior;
* Sistema operacional Windows.

---

## 5. Como preparar o ambiente com Anaconda

### 5.1 Criar um ambiente Conda

Abra o Anaconda Prompt e execute:

```bash
conda create -n ransomware-api-dataset python=3.10
```

### 5.2 Ativar o ambiente

```bash
conda activate ransomware-api-dataset
```

### 5.3 Verificar a versão do Python

```bash
python --version
```

A saída esperada deve ser semelhante a:

```text
Python 3.10.x
```

---

## 6. Como configurar no PyCharm

1. Abra o PyCharm.
2. Clique em **Open**.
3. Selecione a pasta do repositório.
4. Vá em:

```text
File > Settings > Project > Python Interpreter
```

5. Selecione o ambiente Conda criado:

```text
ransomware-api-dataset
```

6. Confirme a configuração.
7. Abra o arquivo:

```text
src/dataser-temporal.py
```

8. Ajuste os caminhos de entrada e saída no final do script.

---

## 7. Configuração dos caminhos

No final do script existe a função `main()`:

```python
def main():
    diretorio_json = r"D:\Mestrado\*.json"
    output_dir = r"D:\Mestrado\datasets_temporais"

    processar_todos_jsons(diretorio_json, output_dir)
```

Esses caminhos devem ser ajustados conforme a máquina onde o artefato será executado.

### Exemplo no Windows

```python
def main():
    diretorio_json = r"C:\Users\usuario\Documents\mestrado\data\raw\*.json"
    output_dir = r"C:\Users\usuario\Documents\mestrado\data\processed"

    processar_todos_jsons(diretorio_json, output_dir)
```

### Exemplo dentro da estrutura do repositório

```python
def main():
    diretorio_json = r"data\raw\*.json"
    output_dir = r"data\processed"

    processar_todos_jsons(diretorio_json, output_dir)
```

---

## 8. Como executar o script

### 8.1 Pelo PyCharm

1. Abra o arquivo `dataser-temporal.py`.
2. Ajuste os caminhos na função `main()`.
3. Clique com o botão direito no arquivo.
4. Selecione:

```text
Run 'dataser-temporal'
```

5. Aguarde o processamento dos arquivos JSON.

---

### 8.2 Pelo terminal

Com o ambiente Conda ativado, execute:

```bash
python src/dataser-temporal.py
```

Exemplo:

```bash
conda activate ransomware-api-dataset
python src/dataser-temporal.py
```

---

## 9. Entrada esperada

O script espera arquivos JSON contendo informações de análise dinâmica.

A estrutura esperada deve conter campos semelhantes a:

```json
{
  "info": {
    "id": "identificador_da_execucao",
    "score": 10
  },
  "target": {
    "file": {
      "name": "amostra.exe"
    }
  },
  "behavior": {
    "processes": [
      {
        "process_name": "amostra.exe",
        "process_id": 1234,
        "parent_id": 1000,
        "first_seen": 1710000000.12345,
        "calls": [
          {
            "api": "CreateFileW",
            "time": 1710000000.22345
          },
          {
            "api": "WriteFile",
            "time": 1710000000.32345
          }
        ]
      }
    ]
  }
}
```

O script também trata variações de nomes para identificadores de processo, como:

```text
process_id
pid
processid
```

E para processo pai:

```text
parent_id
ppid
parent_pid
```

---

## 10. Saídas geradas

Ao final da execução, o script gera os seguintes arquivos:

```text
dataset_processos.csv
dataset_chamadas.csv
geracao_datasets_temporais.log
```

---

# 10.1 Dataset de processos

Arquivo gerado:

```text
dataset_processos.csv
```

Esse dataset contém uma linha por processo observado.

### Colunas geradas

| Coluna                | Descrição                                              |
| --------------------- | ------------------------------------------------------ |
| `exec_id`             | Identificador da execução analisada.                   |
| `exec_name`           | Nome do binário analisado.                             |
| `score_binary`        | Score associado à execução no JSON original.           |
| `process`             | Nome do processo ou linha de comando.                  |
| `command_line`        | Linha de comando do processo.                          |
| `pid`                 | Identificador do processo.                             |
| `parent_id`           | Identificador do processo pai.                         |
| `process_first_seen`  | Timestamp absoluto do primeiro registro do processo.   |
| `first_call_abs_time` | Tempo absoluto da primeira chamada de API do processo. |
| `last_call_abs_time`  | Tempo absoluto da última chamada de API do processo.   |
| `process_start_ms`    | Tempo relativo de início do processo em milissegundos. |
| `process_end_ms`      | Tempo relativo de fim do processo em milissegundos.    |
| `process_duration_ms` | Duração do processo em milissegundos.                  |
| `qtd_api_calls`       | Quantidade de chamadas de API associadas ao processo.  |

---

# 10.2 Dataset de chamadas

Arquivo gerado:

```text
dataset_chamadas.csv
```

Esse dataset contém uma linha por chamada de API observada.

### Colunas geradas

| Coluna               | Descrição                                            |
| -------------------- | ---------------------------------------------------- |
| `exec_id`            | Identificador da execução analisada.                 |
| `exec_name`          | Nome do binário analisado.                           |
| `score_binary`       | Score associado à execução no JSON original.         |
| `process`            | Nome do processo responsável pela chamada.           |
| `command_line`       | Linha de comando do processo.                        |
| `pid`                | Identificador do processo.                           |
| `parent_id`          | Identificador do processo pai.                       |
| `process_first_seen` | Timestamp absoluto do primeiro registro do processo. |
| `api`                | Nome da chamada de API realizada.                    |
| `api_abs_time`       | Tempo absoluto da chamada de API.                    |
| `api_time_ms`        | Tempo relativo da chamada de API em milissegundos.   |

---

## 11. Como o tempo relativo é calculado

O script calcula um tempo inicial global chamado `t0`.

Esse `t0` corresponde ao menor tempo absoluto encontrado entre todas as chamadas de API de todos os processos da execução.

Em seguida, cada chamada de API recebe um tempo relativo em milissegundos:

```text
api_time_ms = (tempo_da_api - t0) * 1000
```

Exemplo:

```text
t0 = 1000.000
tempo_da_api = 1000.250
api_time_ms = 250
```

Isso permite comparar a ordem dos eventos dentro de uma mesma execução, mesmo que os timestamps absolutos sejam grandes ou difíceis de interpretar.

---

## 12. Explicação dos principais trechos do código

### 12.1 Configuração de logs

O script configura logs para exibir informações no terminal e salvar um arquivo `.log`.

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("geracao_datasets_temporais.log", mode="w", encoding="utf-8")
    ]
)
```

Esse trecho permite acompanhar:

* quantos arquivos JSON foram encontrados;
* qual arquivo está sendo processado;
* qual execução está sendo analisada;
* se algum erro ocorreu;
* onde os datasets foram salvos.

---

### 12.2 Formatação de timestamps para Excel

```python
def formatar_timestamp_excel(valor):
    if valor == "" or valor is None:
        return ""
    return f'="{float(valor):.5f}"'
```

Essa função formata timestamps para evitar que o Excel altere ou arredonde valores numéricos grandes automaticamente.

---

### 12.3 Obtenção do PID

```python
def obter_pid(processo: dict):
    return (
        processo.get("process_id")
        or processo.get("pid")
        or processo.get("processid")
        or ""
    )
```

Essa função busca o identificador do processo considerando diferentes nomes possíveis no JSON.

---

### 12.4 Obtenção do processo pai

```python
def obter_parent_id(processo: dict):
    return (
        processo.get("parent_id")
        or processo.get("ppid")
        or processo.get("parent_pid")
        or ""
    )
```

Essa função busca o identificador do processo pai, também considerando variações de nomes.

---

### 12.5 Cálculo do tempo inicial `t0`

```python
def calcular_t0(processos: list[dict]):
    tempos = []

    for processo in processos:
        for call in processo.get("calls", []):
            tempo = call.get("time")
            if tempo is not None:
                tempos.append(tempo)

    if not tempos:
        return None

    return min(tempos)
```

Esse trecho percorre todas as chamadas de API de todos os processos e identifica o menor timestamp encontrado.

Esse valor é usado como referência para calcular os tempos relativos.

---

### 12.6 Extração dos dados do JSON

```python
def extrair_dados_do_json(arquivo_json: str):
```

Essa é a função principal de extração.

Ela:

1. abre o arquivo JSON;
2. extrai informações gerais da execução;
3. identifica os processos;
4. calcula o `t0`;
5. percorre cada processo;
6. calcula tempo inicial, tempo final e duração;
7. gera linhas para o dataset de processos;
8. percorre as chamadas de API;
9. gera linhas para o dataset de chamadas.

---

### 12.7 Geração do dataset de processos

Para cada processo, o script adiciona uma linha em `dataset_processos`:

```python
dataset_processos.append({
    "exec_id": exec_id,
    "exec_name": exec_name,
    "score_binary": score,
    "process": nome_processo,
    "command_line": command_line,
    "pid": pid,
    "parent_id": parent_id,
    "process_first_seen": formatar_timestamp_excel(first_seen),
    "first_call_abs_time": formatar_timestamp_excel(primeiro_tempo),
    "last_call_abs_time": formatar_timestamp_excel(ultimo_tempo),
    "process_start_ms": process_start_ms,
    "process_end_ms": process_end_ms,
    "process_duration_ms": process_duration_ms,
    "qtd_api_calls": len(calls)
})
```

Esse dataset fornece uma visão agregada por processo.

---

### 12.8 Geração do dataset de chamadas

Para cada chamada de API, o script adiciona uma linha em `dataset_chamadas`:

```python
dataset_chamadas.append({
    "exec_id": exec_id,
    "exec_name": exec_name,
    "score_binary": score,
    "process": nome_processo,
    "command_line": command_line,
    "pid": pid,
    "parent_id": parent_id,
    "process_first_seen": formatar_timestamp_excel(first_seen),
    "api": api,
    "api_abs_time": formatar_timestamp_excel(tempo_api),
    "api_time_ms": api_time_ms
})
```

Esse dataset fornece uma visão detalhada de cada chamada de API.

---

### 12.9 Ordenação temporal

O dataset de processos é ordenado por execução e início do processo:

```python
dataset_processos.sort(
    key=lambda x: (
        x["exec_id"],
        x["process_start_ms"] if isinstance(x["process_start_ms"], int) else 10**18
    )
)
```

O dataset de chamadas é ordenado por execução e tempo da chamada:

```python
dataset_chamadas.sort(
    key=lambda x: (
        x["exec_id"],
        x["api_time_ms"]
    )
)
```

Essa ordenação facilita a análise temporal.

---

### 12.10 Salvamento dos arquivos CSV

O script possui duas funções específicas para salvar os datasets:

```python
salvar_dataset_processos()
salvar_dataset_chamadas()
```

Ambas utilizam `csv.DictWriter` para criar os arquivos com cabeçalhos definidos.

Os arquivos são salvos com codificação:

```text
utf-8-sig
```

Essa codificação facilita a abertura dos CSVs no Microsoft Excel.

---

## 13. Exemplo de execução esperada

Após executar o script, o terminal deve exibir mensagens semelhantes a:

```text
2026-01-01 10:00:00 [INFO] 10 arquivo(s) JSON encontrado(s).
2026-01-01 10:00:01 [INFO] [1/10] Processando: exemplo.json
2026-01-01 10:00:01 [INFO] Execução: 123 | Binário: malware.exe | t0: 1710000000.12345
2026-01-01 10:00:10 [INFO] Dataset de processos salvo em: data/processed/dataset_processos.csv
2026-01-01 10:00:10 [INFO] Dataset de chamadas salvo em: data/processed/dataset_chamadas.csv
```

---

## 14. Como validar se funcionou

Após a execução, verifique se os arquivos foram gerados no diretório de saída:

```text
dataset_processos.csv
dataset_chamadas.csv
geracao_datasets_temporais.log
```

Também é possível abrir os arquivos CSV no Excel, LibreOffice Calc ou em uma biblioteca como Pandas.

Exemplo de validação com Python:

```python
import pandas as pd

processos = pd.read_csv("data/processed/dataset_processos.csv")
chamadas = pd.read_csv("data/processed/dataset_chamadas.csv")

print(processos.head())
print(chamadas.head())

print(processos.shape)
print(chamadas.shape)
```

---

## 15. Limitações atuais

A versão atual do artefato possui algumas limitações:

1. Os caminhos de entrada e saída estão definidos diretamente no código.
2. O script ainda não possui interface por linha de comando com argumentos.
3. A classificação comportamental das API calls ainda não está implementada.
4. O script depende da estrutura do JSON de entrada.
5. Arquivos JSON sem chamadas de API são ignorados.
6. Ainda não há testes automatizados.
7. Ainda não há Dockerfile para execução isolada.

Essas limitações são conhecidas e serão tratadas em versões futuras do artefato.

---

## 16. Melhorias futuras planejadas

As próximas melhorias previstas são:

* adicionar argumentos por linha de comando;
* permitir configuração por arquivo `.yaml`;
* implementar classificação das API calls por categoria comportamental;
* gerar relatório estatístico automático;
* adicionar testes automatizados;
* incluir exemplos de entrada e saída;
* criar documentação específica para reprodutibilidade;
* adicionar suporte a Docker;
* gerar gráficos temporais;
* correlacionar dataset de chamadas com dataset de processos;
* preparar o artefato para avaliação científica.

---

# 17. Avaliação de artefatos

Este repositório foi organizado considerando critérios de avaliação de artefatos científicos, com foco nos seguintes selos:

* **SeloD — Artefatos Disponíveis**
* **SeloF — Artefatos Funcionais**
* **SeloS — Artefatos Sustentáveis**
* **SeloR — Experimentos Reprodutíveis**

---

## 17.1 SeloD — Artefato Disponível

Para atender ao critério de disponibilidade, este repositório deve conter:

* código-fonte público;
* licença de uso;
* documentação de instalação;
* documentação de execução;
* arquivos de exemplo;
* descrição do artefato;
* instruções para citação.

Itens recomendados:

```text
README.md
LICENSE
CITATION.cff
artifact/ARTIFACT.md
data/README.md
```

---

## 17.2 SeloF — Artefato Funcional

Para atender ao critério de funcionalidade, o artefato deve ser executável por avaliadores externos.

Este README descreve:

* ambiente utilizado;
* requisitos;
* configuração com Anaconda;
* configuração com PyCharm;
* formato esperado dos dados;
* comandos de execução;
* arquivos gerados;
* validação da saída.

O comportamento esperado é:

```text
Entrada: arquivos JSON de análise dinâmica
Saída 1: dataset_processos.csv
Saída 2: dataset_chamadas.csv
Saída 3: geracao_datasets_temporais.log
```

---

## 17.3 SeloS — Artefato Sustentável

Para atender ao critério de sustentabilidade, o projeto deve ser organizado de forma modular, documentada e extensível.

Boas práticas adotadas ou recomendadas:

* separação entre código, dados, documentação e resultados;
* uso de nomes claros para arquivos e funções;
* documentação das colunas dos datasets;
* uso de logs para rastrear execução;
* ausência de dependências externas desnecessárias;
* planejamento de testes automatizados;
* documentação das limitações.

---

## 17.4 SeloR — Experimentos Reprodutíveis

Para atender ao critério de reprodutibilidade, o artefato deve permitir que outros pesquisadores reproduzam os resultados.

Para isso, recomenda-se incluir:

```text
artifact/REPRODUCIBILITY.md
data/raw/exemplo.json
data/processed/dataset_processos.csv
data/processed/dataset_chamadas.csv
results/logs/
```

Um avaliador deve conseguir executar:

```bash
python src/dataser-temporal.py
```

E obter os mesmos arquivos de saída para os dados de exemplo fornecidos.

---

## 18. Checklist de avaliação

### SeloD — Disponibilidade

* [ ] Repositório público no GitHub.
* [ ] Código-fonte disponível.
* [ ] Licença definida.
* [ ] README completo.
* [ ] Dados de exemplo disponíveis.
* [ ] Instruções de citação disponíveis.

### SeloF — Funcionalidade

* [ ] Ambiente descrito.
* [ ] Instruções de instalação disponíveis.
* [ ] Instruções de execução disponíveis.
* [ ] Exemplo de entrada disponível.
* [ ] Exemplo de saída disponível.
* [ ] Logs gerados automaticamente.

### SeloS — Sustentabilidade

* [ ] Estrutura do projeto organizada.
* [ ] Código comentado e legível.
* [ ] Documentação das colunas dos datasets.
* [ ] Limitações documentadas.
* [ ] Melhorias futuras listadas.
* [ ] Testes planejados ou implementados.

### SeloR — Reprodutibilidade

* [ ] Dados de exemplo incluídos.
* [ ] Script executável.
* [ ] Saídas esperadas documentadas.
* [ ] Resultados reproduzíveis a partir dos exemplos.
* [ ] Ambiente de execução documentado.
* [ ] Logs preservados para auditoria.

---

## 19. Cuidados de segurança

Este repositório não deve conter:

* amostras reais de ransomware;
* executáveis maliciosos;
* credenciais;
* dados pessoais;
* logs com caminhos sensíveis;
* informações confidenciais de ambientes reais.

Caso sejam utilizados dados reais de análise dinâmica, recomenda-se anonimizar nomes de arquivos, caminhos, usuários e identificadores sensíveis.

---

## 20. Licença

Recomenda-se utilizar uma licença aberta, como:

```text
MIT License
```

ou

```text
Apache License 2.0
```

---

## 21. Como citar

Caso utilize este artefato em trabalhos acadêmicos, cite o repositório conforme o arquivo `CITATION.cff`.

Exemplo:

```text
Autor. Ransomware Temporal API Dataset Generator. GitHub, 2026.
```

---

## 22. Status do artefato

Status atual:

```text
Versão inicial funcional para geração de datasets temporais.
```

Próxima etapa:

```text
Implementar classificação comportamental das API calls e correlação com os processos.
```

