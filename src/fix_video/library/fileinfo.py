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
