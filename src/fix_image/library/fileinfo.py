import re
from datetime import datetime
from pathlib import Path

from dateparser.search import search_dates

from ..setup import DATE_STANDARD


def limpar_e_normalizar_nome_arquivo(
    file_path: str | Path,
    preferir_ultima_data: bool = True,  # True = pega a última data encontrada
    # formato_data_hora: str = "{date}_{time}" if time else "{date}",  # placeholder
    formato_saida: str = "{data_hora} - {base}.fixed{ext}",
    preferir_iso: bool = False,  # False = yyyymmdd, True = yyyy-mm-dd
) -> str:
    """
    Retorna o novo nome sugerido com data no formato YYYYMMDD ou YYYY-MM-DD
    Remove a data original detectada do nome.
    Retorna None se não encontrou data válida.
    """
    caminho = Path(file_path)
    nome_original = caminho.stem  # sem extensão
    extensao = caminho.suffix.lower()

    tentativas = ["", "_"]
    for i, tentativa in enumerate(tentativas):
        if i > 0:
            _nome = nome_original.replace(tentativa, " ")
        else:
            _nome = nome_original

        # Tenta encontrar TODAS as datas no nome do arquivo
        encontradas = search_dates(
            _nome,
            languages=["pt", "en"],  # português + inglês (muito comum)
            settings={
                "DATE_ORDER": "DMY",  # importante para Brasil
                "PREFER_LOCALE_DATE_ORDER": True,
                "STRICT_PARSING": False,
                "RETURN_AS_TIMEZONE_AWARE": False,
                "PREFER_DAY_OF_MONTH": "current",  # evita chutar dias
            },
        )

        if encontradas:
            break

    if not encontradas:
        # Monta o novo nome
        nome_limpo = caminho.stem
        dt = get_early_time(caminho, formatted=False)

        # Formata a data no padrão desejado
        if preferir_iso:
            data_formatada = dt.strftime("%Y-%m-%d")
        else:
            data_formatada = dt.strftime("%Y.%m.%d")

        novo_nome = formato_saida.format(data_hora=data_formatada, base=nome_limpo, ext=extensao)

        return novo_nome  # nenhuma data detectada

    # Escolhe qual data usar (última ou primeira)
    if preferir_ultima_data:
        texto_data, dt = encontradas[-1]
    else:
        texto_data, dt = encontradas[0]

    # Formata a data no padrão desejado
    if preferir_iso:
        data_formatada = dt.strftime("%Y-%m-%d")
    else:
        data_formatada = dt.strftime("%Y.%m.%d")

    # Remove o trecho exato que foi reconhecido como data
    # Usamos re.escape para escapar caracteres especiais (. - _ etc)
    padrao = re.escape(texto_data)
    nome_limpo = re.sub(padrao, "", nome_original, count=1).strip()

    # Remove separadores duplicados ou sobrando no início/fim
    nome_limpo = re.sub(r"[-_. ]{2,}", " ", nome_limpo).strip(" -_.")
    if not nome_limpo:
        nome_limpo = "arquivo"

    # Monta o novo nome
    novo_nome = formato_saida.format(data_hora=data_formatada, base=nome_limpo, ext=extensao)

    return novo_nome


def _extrair_hora_do_nome(nome: str, texto_encontrado: str) -> str | None:
    """
    Tenta extrair hora do nome do arquivo usando padrões comuns.
    Procura por padrões próximos ao texto de data detectado.

    Padrões reconhecidos:
        14h35, 14H35
        14:35, 14.35
        14-35
        143500, 143545
        às 14:35, às 14-35
    """
    # Encontra a posição do texto de data no nome
    pos = nome.find(texto_encontrado)
    if pos == -1:
        return None

    # Procura por hora próxima à data (antes ou depois)
    contexto_antes = nome[:pos] if pos > 0 else ""
    contexto_depois = nome[pos + len(texto_encontrado) :]
    contexto_completo = contexto_antes + " " + contexto_depois

    # Padrões de hora: HHhMM, HH:MM, HH.MM, HH-MM, HHMMSS
    padroes = [
        (r"(\d{1,2})[hH](\d{2})", "%H%M"),  # 14h35 ou 14H35
        (r"(\d{1,2}):(\d{2})(?::(\d{2}))?", None),  # 14:35 ou 14:35:30
        (r"(\d{1,2})\.(\d{2})(?:\.(\d{2}))?", "%H%M"),  # 14.35 ou 14.35.30
        (r"(\d{1,2})-(\d{2})(?:-(\d{2}))?", "%H%M"),  # 14-35 ou 14-35-30
        (r"(\d{6})", "%H%M%S"),  # 143500
    ]

    for padrao, formato in padroes:
        match = re.search(padrao, contexto_completo)
        if match:
            grupos = match.groups()
            try:
                h = int(grupos[0])
                m = int(grupos[1]) if len(grupos) > 1 else 0
                s = int(grupos[2]) if len(grupos) > 2 else 0

                # Valida os valores
                if 0 <= h <= 23 and 0 <= m <= 59 and 0 <= s <= 59:
                    if s > 0:
                        return f"{h:02d}{m:02d}{s:02d}"
                    else:
                        return f"{h:02d}{m:02d}"
            except (ValueError, IndexError):
                continue

    return None


def blimpar_e_normalizar_nome_arquivo(
    caminho: str | Path,
    idiomas_prioritarios: list[str] = ["pt", "en"],
    preferir_ultima_data: bool = True,
    formato_saida: str = "{data_hora} - {nome_limpo}{ext}",
    manter_segundos: bool = False,
) -> str | None:
    """
    Extrai data (e hora se existir) do nome do arquivo,
    remove o trecho detectado e sugere novo nome com data no início.

    Retorna:
        - novo nome sugerido (str)
        - None se não encontrou data válida

    Exemplos de padrões reconhecidos:
        2024-05-17
        17.05.2024
        17-05-2024
        17_05_2024
        20240517
        17jan2024
        17 de maio de 2024
        foto 15.10.2023 14h35
        IMG_20250630_183245
        relatorio 2024.08.12 às 09-15 v2
        2024-05-17 14:35:45
        2024-05-17T14:35:45
    """
    caminho = Path(caminho)
    nome = caminho.stem
    ext = caminho.suffix

    # Busca todas as datas/horas detectáveis
    resultados = search_dates(
        nome,
        languages=idiomas_prioritarios,
        settings={
            "DATE_ORDER": "DMY",  # padrão BR/PT
            "PREFER_LOCALE_DATE_ORDER": True,
            "STRICT_PARSING": False,
            "PREFER_DAY_OF_MONTH": "current",
            "RETURN_AS_TIMEZONE_AWARE": False,
            "DEFAULT_LANGUAGES": idiomas_prioritarios,
        },
    )

    if not resultados:
        # Monta o novo nome
        nome_limpo = caminho.stem
        dt = get_early_time(caminho, formatted=False)

        # Formata a data no padrão desejado
        data_str = dt.strftime("%Y%m%d")

        novo_nome = formato_saida.format(data_hora=data_str, nome_limpo=nome_limpo, ext=ext)

        return novo_nome  # nenhuma data detectada

    # Escolhe a data mais provável (geralmente a última em nomes de arquivo)
    if preferir_ultima_data:
        texto_encontrado, dt = resultados[-1]
    else:
        texto_encontrado, dt = resultados[0]

    # Formata a parte da data
    data_str = dt.strftime("%Y%m%d")

    # Tenta extrair hora do dateparser primeiro
    hora_str = ""
    if dt.hour > 0 or dt.minute > 0 or dt.second > 0:
        # Hora foi detectada pelo dateparser
        if manter_segundos and dt.second > 0:
            hora_str = dt.strftime("%H%M%S")
        else:
            hora_str = dt.strftime("%H%M")
    else:
        # Tenta extrair hora manualmente procurando padrões no nome
        hora_extraida = _extrair_hora_do_nome(nome, texto_encontrado)
        if hora_extraida:
            hora_str = hora_extraida

    data_hora = f"{data_str}_{hora_str}" if hora_str else data_str

    # Remove exatamente o texto que foi reconhecido
    # Escapamos caracteres especiais para não quebrar a regex
    texto_escaped = re.escape(texto_encontrado)
    nome_limpo = re.sub(texto_escaped, "", nome, count=1)

    # Limpeza adicional: remove separadores duplicados / sobrando
    # Ex: "foto  -  relatório" → "foto relatório"
    nome_limpo = re.sub(r"[-_. ]{2,}", " ", nome_limpo)  # junta múltiplos separadores
    nome_limpo = re.sub(r"^[-_. ]+|[-_. ]+$", "", nome_limpo)  # remove bordas
    nome_limpo = nome_limpo.strip()

    if not nome_limpo:
        nome_limpo = "arquivo"

    # Monta o nome final
    novo_nome = formato_saida.format(data_hora=data_hora, nome_limpo=nome_limpo, ext=ext)

    return novo_nome


def get_early_time(file_path: Path, formatted=True):
    """
    Retorna as datas de criação e modificação de um arquivo.
    """
    stat_info = file_path.stat()
    # date_from_name = get_date_from_filename(file_path)
    # if date_from_name is None:
    #     date_from_name = datetime.now()
    creation_time = datetime.fromtimestamp(stat_info.st_birthtime)
    modification_time = datetime.fromtimestamp(stat_info.st_mtime)
    access_time = datetime.fromtimestamp(stat_info.st_atime)

    # Encontra a data mais antiga
    min_date = min(creation_time, modification_time, access_time)
    if formatted:
        return min_date.strftime(DATE_STANDARD)
    else:
        return min_date


def has_date_in_filename(file_path: Path) -> bool:
    return bool(get_date_from_filename(file_path))


def get_date_from_filename(file_path: Path):
    """
    Tenta extrair uma data do nome do arquivo no formato YYYYMMDD.
    Retorna None se não encontrar.
    """
    name = file_path.stem

    # yyyy-mm-dd hh.mi.ss (com hora)
    match = re.search(r"(\d{4})-(\d{2})-(\d{2})\s+(\d{2})\.(\d{2})\.(\d{2})", name)
    if match:
        try:
            data_str = (
                f"{match.group(1)}-{match.group(2)}-{match.group(3)} {match.group(4)}:{match.group(5)}:{match.group(6)}"
            )
            data = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
            return data
        except ValueError:
            pass

    # yyyy-mm-dd hh-mi-ss (com hifen)
    match = re.search(r"(\d{4})-(\d{2})-(\d{2})\s+(\d{2})-(\d{2})-(\d{2})", name)
    if match:
        try:
            data_str = (
                f"{match.group(1)}-{match.group(2)}-{match.group(3)} {match.group(4)}:{match.group(5)}:{match.group(6)}"
            )
            data = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
            return data
        except ValueError:
            pass

    # yyyy-mm-dd (sem hora)
    match = re.search(r"(\d{4})-(\d{2})-(\d{2})", name)
    if match:
        try:
            data = datetime.strptime(match.group(0), "%Y-%m-%d")
            return data
        except ValueError:
            pass

    # yyyymmdd
    match = re.search(r"(\d{8})", name)
    if match:
        try:
            data = datetime.strptime(match.group(0), "%Y%m%d")
            return data
        except ValueError:
            pass

    # dd-mm-yy
    match = re.search(r"(\d{2})-(\d{2})-(\d{2})", name)
    if match:
        try:
            data = datetime.strptime(match.group(0), "%d-%m-%y")
            return data
        except ValueError:
            pass

    return None


def remover_data_do_arquivo(nome_arquivo):
    """Remove padrões de data do nome do arquivo"""

    # yyyy-mm-dd hh.mi.ss (com hora e ponto)
    resultado = re.sub(r"\s*\d{4}-\d{2}-\d{2}\s+\d{2}\.\d{2}\.\d{2}", "", nome_arquivo)

    # yyyy-mm-dd hh:mi:ss (com hora e dois pontos)
    if resultado == nome_arquivo:
        resultado = re.sub(r"\s*\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}", "", nome_arquivo)

    # yyyy-mm-dd (apenas data)
    if resultado == nome_arquivo:
        resultado = re.sub(r"\s*\d{4}-\d{2}-\d{2}", "", nome_arquivo)

    # yyyymmdd
    if resultado == nome_arquivo:
        resultado = re.sub(r"\b\d{8}\b", "", nome_arquivo)

    # dd-mm-yy
    if resultado == nome_arquivo:
        resultado = re.sub(r"\d{2}-\d{2}-\d{2}", "", nome_arquivo)

    # Limpar espaços/underscores duplicados deixados para trás
    resultado = re.sub(r"[\s_]+", "_", resultado).strip("_")
    resultado = re.sub(r"_\.", ".", resultado)  # Remove underscore antes de extensão

    return resultado
