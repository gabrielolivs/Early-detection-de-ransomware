import glob
import json
import csv
import os
import logging
from pathlib import Path
from collections import Counter, defaultdict

import yaml


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("geracao_datasets_temporais.log", mode="w", encoding="utf-8")
    ]
)

logger = logging.getLogger(__name__)


def formatar_timestamp_excel(valor):
    if valor == "" or valor is None:
        return ""
    return f'="{float(valor):.5f}"'


def obter_pid(processo: dict):
    return (
        processo.get("process_id")
        or processo.get("pid")
        or processo.get("processid")
        or ""
    )


def obter_parent_id(processo: dict):
    return (
        processo.get("parent_id")
        or processo.get("ppid")
        or processo.get("parent_pid")
        or ""
    )


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


# ============================================================
# LEITURA FLEXÍVEL DE JSON
# ============================================================

def carregar_json_com_encoding_flexivel(arquivo_json: str):
    """
    Tenta carregar um JSON usando diferentes codificações.

    Alguns relatórios podem não estar em UTF-8 puro.
    Por isso, tentamos UTF-8 e depois alternativas comuns no Windows.
    """
    tentativas = [
        ("utf-8", "strict"),
        ("utf-8-sig", "strict"),
        ("cp1252", "strict"),
        ("latin-1", "strict"),
        ("utf-8", "replace"),
    ]

    ultimo_erro = None

    for encoding, errors in tentativas:
        try:
            logger.info(f"Tentando ler {Path(arquivo_json).name} com encoding={encoding}, errors={errors}")

            with open(arquivo_json, "r", encoding=encoding, errors=errors) as f:
                return json.load(f)

        except UnicodeDecodeError as e:
            ultimo_erro = e
            logger.warning(
                f"Falha de encoding ao ler {arquivo_json} com {encoding}/{errors}: {e}"
            )

        except json.JSONDecodeError as e:
            ultimo_erro = e
            logger.warning(
                f"Falha ao interpretar JSON em {arquivo_json} com {encoding}/{errors}: {e}"
            )

        except OSError as e:
            ultimo_erro = e
            logger.warning(
                f"Erro de sistema ao abrir {arquivo_json}: {e}"
            )
            break

    raise ultimo_erro


# ============================================================
# CLASSIFICAÇÃO DAS API CALLS
# ============================================================

def normalizar_nome_api(api_name: str) -> str:
    """
    Normaliza o nome da API para comparação.
    Exemplo:
    CreateFileW -> createfilew
    """
    if api_name is None:
        return ""

    return str(api_name).strip().lower()


def carregar_mapeamento_categorias(caminho_yaml: str) -> dict:
    """
    Lê o arquivo YAML de categorias e cria um dicionário invertido.

    Exemplo de entrada YAML:
    Arquivo:
      - CreateFileW
      - ReadFile

    Saída esperada:
    {
      "createfilew": "Arquivo",
      "readfile": "Arquivo"
    }
    """
    if not os.path.exists(caminho_yaml):
        raise FileNotFoundError(f"Arquivo de categorias não encontrado: {caminho_yaml}")

    with open(caminho_yaml, "r", encoding="utf-8") as f:
        categorias = yaml.safe_load(f)

    if not categorias:
        raise ValueError(f"Arquivo de categorias vazio ou inválido: {caminho_yaml}")

    api_para_categoria = {}

    for categoria, apis in categorias.items():
        if not isinstance(apis, list):
            logger.warning(f"Categoria ignorada por formato inválido: {categoria}")
            continue

        for api in apis:
            api_normalizada = normalizar_nome_api(api)

            if api_normalizada:
                api_para_categoria[api_normalizada] = categoria

    logger.info(f"{len(api_para_categoria)} API calls carregadas do arquivo de categorias.")

    return api_para_categoria


def classificar_api(api_name: str, api_para_categoria: dict) -> str:
    """
    Classifica uma API call com base no mapeamento local.
    """
    api_normalizada = normalizar_nome_api(api_name)

    if not api_normalizada:
        return "Desconhecida"

    return api_para_categoria.get(api_normalizada, "Não classificada")


def salvar_unknown_api_calls(dataset_chamadas: list[dict], output_csv: str):
    """
    Salva as APIs que não foram classificadas, com contagem de ocorrência.
    """
    contador = Counter()

    for linha in dataset_chamadas:
        if linha.get("api_category") == "Não classificada":
            contador[linha.get("api", "")] += 1

    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
        colunas = ["api", "qtd_ocorrencias"]
        writer = csv.DictWriter(f, fieldnames=colunas)
        writer.writeheader()

        for api, qtd in contador.most_common():
            writer.writerow({
                "api": api,
                "qtd_ocorrencias": qtd
            })

    logger.info(f"APIs não classificadas salvas em: {output_csv}")


def salvar_resumo_categorias(dataset_chamadas: list[dict], output_csv: str):
    """
    Salva um resumo geral com a quantidade de chamadas por categoria.
    """
    contador = Counter()

    for linha in dataset_chamadas:
        categoria = linha.get("api_category", "Desconhecida")
        contador[categoria] += 1

    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
        colunas = ["api_category", "qtd_chamadas"]
        writer = csv.DictWriter(f, fieldnames=colunas)
        writer.writeheader()

        for categoria, qtd in contador.most_common():
            writer.writerow({
                "api_category": categoria,
                "qtd_chamadas": qtd
            })

    logger.info(f"Resumo de categorias salvo em: {output_csv}")


# ============================================================
# ANÁLISE TEMPORAL POR JANELAS
# ============================================================

def obter_janela_temporal(api_time_ms: int, tamanho_janela_ms: int = 5000):
    """
    Calcula a janela temporal de uma chamada de API.

    Exemplo com janela de 5000 ms:
    0 até 4999 ms      -> 0-5s
    5000 até 9999 ms   -> 5-10s
    10000 até 14999 ms -> 10-15s
    """
    if api_time_ms is None or api_time_ms == "":
        return None, None, "sem_janela"

    inicio_ms = (int(api_time_ms) // tamanho_janela_ms) * tamanho_janela_ms
    fim_ms = inicio_ms + tamanho_janela_ms

    inicio_s = inicio_ms // 1000
    fim_s = fim_ms // 1000

    label = f"{inicio_s}-{fim_s}s"

    return inicio_ms, fim_ms, label


def salvar_resumo_temporal_categorias(
    dataset_chamadas: list[dict],
    output_csv: str,
    tamanho_janela_ms: int = 5000
):
    """
    Gera um CSV contando as categorias de API por janela temporal,
    considerando a execução como um todo.

    Saída:
    exec_id | exec_name | janela | total_api_calls | Arquivo | Registro | Processo | ...
    """
    agregacao = defaultdict(Counter)
    categorias_encontradas = set()

    for linha in dataset_chamadas:
        exec_id = linha.get("exec_id", "")
        exec_name = linha.get("exec_name", "")
        api_time_ms = linha.get("api_time_ms", "")
        categoria = linha.get("api_category", "Não classificada")

        janela_inicio_ms, janela_fim_ms, janela_label = obter_janela_temporal(
            api_time_ms,
            tamanho_janela_ms
        )

        chave = (
            exec_id,
            exec_name,
            janela_inicio_ms,
            janela_fim_ms,
            janela_label
        )

        agregacao[chave][categoria] += 1
        categorias_encontradas.add(categoria)

    categorias_ordenadas = sorted(categorias_encontradas)

    colunas = [
        "exec_id",
        "exec_name",
        "janela_inicio_ms",
        "janela_fim_ms",
        "janela",
        "total_api_calls"
    ] + categorias_ordenadas

    linhas_saida = []

    for chave, contador in agregacao.items():
        exec_id, exec_name, janela_inicio_ms, janela_fim_ms, janela_label = chave

        total_api_calls = sum(contador.values())

        linha_saida = {
            "exec_id": exec_id,
            "exec_name": exec_name,
            "janela_inicio_ms": janela_inicio_ms,
            "janela_fim_ms": janela_fim_ms,
            "janela": janela_label,
            "total_api_calls": total_api_calls
        }

        for categoria in categorias_ordenadas:
            linha_saida[categoria] = contador.get(categoria, 0)

        linhas_saida.append(linha_saida)

    linhas_saida.sort(
        key=lambda x: (
            x["exec_id"],
            x["janela_inicio_ms"] if isinstance(x["janela_inicio_ms"], int) else 10**18
        )
    )

    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=colunas)
        writer.writeheader()
        writer.writerows(linhas_saida)

    logger.info(f"Resumo temporal por janela salvo em: {output_csv}")


def salvar_resumo_temporal_categorias_por_processo(
    dataset_chamadas: list[dict],
    output_csv: str,
    tamanho_janela_ms: int = 5000
):
    """
    Gera um CSV contando as categorias de API por janela temporal e por processo.

    Saída:
    exec_id | exec_name | process | pid | janela | total_api_calls | Arquivo | Registro | ...
    """
    agregacao = defaultdict(Counter)
    categorias_encontradas = set()

    for linha in dataset_chamadas:
        exec_id = linha.get("exec_id", "")
        exec_name = linha.get("exec_name", "")
        process = linha.get("process", "")
        pid = linha.get("pid", "")
        parent_id = linha.get("parent_id", "")
        api_time_ms = linha.get("api_time_ms", "")
        categoria = linha.get("api_category", "Não classificada")

        janela_inicio_ms, janela_fim_ms, janela_label = obter_janela_temporal(
            api_time_ms,
            tamanho_janela_ms
        )

        chave = (
            exec_id,
            exec_name,
            process,
            pid,
            parent_id,
            janela_inicio_ms,
            janela_fim_ms,
            janela_label
        )

        agregacao[chave][categoria] += 1
        categorias_encontradas.add(categoria)

    categorias_ordenadas = sorted(categorias_encontradas)

    colunas = [
        "exec_id",
        "exec_name",
        "process",
        "pid",
        "parent_id",
        "janela_inicio_ms",
        "janela_fim_ms",
        "janela",
        "total_api_calls"
    ] + categorias_ordenadas

    linhas_saida = []

    for chave, contador in agregacao.items():
        (
            exec_id,
            exec_name,
            process,
            pid,
            parent_id,
            janela_inicio_ms,
            janela_fim_ms,
            janela_label
        ) = chave

        total_api_calls = sum(contador.values())

        linha_saida = {
            "exec_id": exec_id,
            "exec_name": exec_name,
            "process": process,
            "pid": pid,
            "parent_id": parent_id,
            "janela_inicio_ms": janela_inicio_ms,
            "janela_fim_ms": janela_fim_ms,
            "janela": janela_label,
            "total_api_calls": total_api_calls
        }

        for categoria in categorias_ordenadas:
            linha_saida[categoria] = contador.get(categoria, 0)

        linhas_saida.append(linha_saida)

    linhas_saida.sort(
        key=lambda x: (
            x["exec_id"],
            x["process"],
            x["pid"],
            x["janela_inicio_ms"] if isinstance(x["janela_inicio_ms"], int) else 10**18
        )
    )

    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=colunas)
        writer.writeheader()
        writer.writerows(linhas_saida)

    logger.info(f"Resumo temporal por processo salvo em: {output_csv}")


# ============================================================
# EXTRAÇÃO DOS DADOS DO JSON
# ============================================================

def extrair_dados_do_json(arquivo_json: str, api_para_categoria: dict):
    dataset_processos = []
    dataset_chamadas = []

    try:
        data = carregar_json_com_encoding_flexivel(arquivo_json)

        exec_id = data.get("info", {}).get("id")
        exec_name = data.get("target", {}).get("file", {}).get("name")
        score = data.get("info", {}).get("score")
        processos = data.get("behavior", {}).get("processes", [])

        t0 = calcular_t0(processos)

        if t0 is None:
            logger.warning(f"Nenhuma chamada encontrada no arquivo: {arquivo_json}")
            return [], []

        logger.info("=" * 100)
        logger.info(f"Arquivo: {arquivo_json}")
        logger.info(f"Execução: {exec_id} | Binário: {exec_name} | t0: {t0}")

        for processo in processos:
            process_name = processo.get("process_name", "")
            command_line = processo.get("command_line", "")
            pid = obter_pid(processo)
            parent_id = obter_parent_id(processo)
            first_seen = processo.get("first_seen", "")
            calls = processo.get("calls", [])

            nome_processo = process_name or command_line or "SEM_NOME"

            tempos_chamadas = [
                call.get("time")
                for call in calls
                if call.get("time") is not None
            ]

            if tempos_chamadas:
                primeiro_tempo = min(tempos_chamadas)
                ultimo_tempo = max(tempos_chamadas)

                process_start_ms = int(round((primeiro_tempo - t0) * 1000))
                process_end_ms = int(round((ultimo_tempo - t0) * 1000))
                process_duration_ms = process_end_ms - process_start_ms
            else:
                primeiro_tempo = ""
                ultimo_tempo = ""
                process_start_ms = ""
                process_end_ms = ""
                process_duration_ms = ""

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

            for call in calls:
                api = call.get("api")
                tempo_api = call.get("time")

                if api is None or tempo_api is None:
                    continue

                api_time_ms = int(round((tempo_api - t0) * 1000))
                api_category = classificar_api(api, api_para_categoria)

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
                    "api_category": api_category,
                    "api_abs_time": formatar_timestamp_excel(tempo_api),
                    "api_time_ms": api_time_ms
                })

        dataset_processos.sort(
            key=lambda x: (
                x["exec_id"],
                x["process_start_ms"] if isinstance(x["process_start_ms"], int) else 10**18
            )
        )

        dataset_chamadas.sort(
            key=lambda x: (
                x["exec_id"],
                x["api_time_ms"]
            )
        )

    except (json.JSONDecodeError, UnicodeDecodeError, OSError, KeyError, TypeError) as e:
        logger.warning(f"Erro ao processar {arquivo_json}: {e}")

    return dataset_processos, dataset_chamadas


# ============================================================
# SALVAMENTO DOS DATASETS
# ============================================================

def salvar_dataset_processos(linhas: list[dict], output_csv: str):
    colunas = [
        "exec_id",
        "exec_name",
        "score_binary",
        "process",
        "command_line",
        "pid",
        "parent_id",
        "process_first_seen",
        "first_call_abs_time",
        "last_call_abs_time",
        "process_start_ms",
        "process_end_ms",
        "process_duration_ms",
        "qtd_api_calls"
    ]

    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=colunas)
        writer.writeheader()
        writer.writerows(linhas)


def salvar_dataset_chamadas(linhas: list[dict], output_csv: str):
    colunas = [
        "exec_id",
        "exec_name",
        "score_binary",
        "process",
        "command_line",
        "pid",
        "parent_id",
        "process_first_seen",
        "api",
        "api_category",
        "api_abs_time",
        "api_time_ms"
    ]

    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=colunas)
        writer.writeheader()
        writer.writerows(linhas)


# ============================================================
# PROCESSAMENTO DE TODOS OS JSONS
# ============================================================

def processar_todos_jsons(diretorio_json: str, output_dir: str, caminho_categorias: str):
    os.makedirs(output_dir, exist_ok=True)

    api_para_categoria = carregar_mapeamento_categorias(caminho_categorias)

    arquivos_json = glob.glob(diretorio_json)

    if not arquivos_json:
        logger.error(f"Nenhum JSON encontrado em: {diretorio_json}")
        return

    logger.info(f"{len(arquivos_json)} arquivo(s) JSON encontrado(s).")
    logger.info(f"Arquivo de categorias utilizado: {caminho_categorias}")

    dataset_processos_final = []
    dataset_chamadas_final = []

    for idx, arquivo in enumerate(arquivos_json, start=1):
        logger.info(f"[{idx}/{len(arquivos_json)}] Processando: {Path(arquivo).name}")

        processos, chamadas = extrair_dados_do_json(
            arquivo_json=arquivo,
            api_para_categoria=api_para_categoria
        )

        dataset_processos_final.extend(processos)
        dataset_chamadas_final.extend(chamadas)

    dataset_processos_final.sort(
        key=lambda x: (
            x["exec_id"],
            x["process_start_ms"] if isinstance(x["process_start_ms"], int) else 10**18
        )
    )

    dataset_chamadas_final.sort(
        key=lambda x: (
            x["exec_id"],
            x["api_time_ms"]
        )
    )

    output_processos = os.path.join(output_dir, "dataset_processos.csv")
    output_chamadas = os.path.join(output_dir, "dataset_chamadas_classificado.csv")
    output_unknown = os.path.join(output_dir, "unknown_api_calls.csv")
    output_resumo = os.path.join(output_dir, "resumo_categorias_api.csv")
    output_temporal = os.path.join(output_dir, "resumo_temporal_categorias.csv")
    output_temporal_processo = os.path.join(output_dir, "resumo_temporal_categorias_por_processo.csv")

    salvar_dataset_processos(dataset_processos_final, output_processos)
    salvar_dataset_chamadas(dataset_chamadas_final, output_chamadas)
    salvar_unknown_api_calls(dataset_chamadas_final, output_unknown)
    salvar_resumo_categorias(dataset_chamadas_final, output_resumo)

    salvar_resumo_temporal_categorias(
        dataset_chamadas=dataset_chamadas_final,
        output_csv=output_temporal,
        tamanho_janela_ms=5000
    )

    salvar_resumo_temporal_categorias_por_processo(
        dataset_chamadas=dataset_chamadas_final,
        output_csv=output_temporal_processo,
        tamanho_janela_ms=5000
    )

    logger.info(f"Dataset de processos salvo em: {output_processos}")
    logger.info(f"Dataset de chamadas classificado salvo em: {output_chamadas}")
    logger.info(f"APIs não classificadas salvas em: {output_unknown}")
    logger.info(f"Resumo de categorias salvo em: {output_resumo}")
    logger.info(f"Resumo temporal por janela salvo em: {output_temporal}")
    logger.info(f"Resumo temporal por processo salvo em: {output_temporal_processo}")
    logger.info(f"Total de chamadas processadas: {len(dataset_chamadas_final)}")


# ============================================================
# MAIN
# ============================================================

def main():
    diretorio_json = r"D:\Mestrado\*.json"
    output_dir = r"D:\Mestrado\datasets_temporais"
    caminho_categorias = r"D:\Mestrado\api_categories.yaml"

    processar_todos_jsons(
        diretorio_json=diretorio_json,
        output_dir=output_dir,
        caminho_categorias=caminho_categorias
    )


if __name__ == "__main__":
    main()

