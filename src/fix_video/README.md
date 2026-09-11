# fix_video

Ferramenta de linha de comando para corrigir, acelerar e comprimir vídeos usando **FFmpeg** (e, quando necessário, **untrunc**). Normaliza os arquivos processados, opcionalmente renomeia com a data do conteúdo, adiciona metadados de controle e gera relatórios em JSON de tudo que foi feito.

Foi criada para resolver o problema de vídeos que ficam com defeito/gigantes depois de baixados por ferramentas como o CocoCut.

## Sumário

- [Como funciona](#como-funciona)
- [Modos de execução](#modos-de-execução)
- [Convenção de nomes e metadados](#convenção-de-nomes-e-metadados)
- [Relatórios gerados](#relatórios-gerados)
- [Requisitos](#requisitos)
- [Uso via CLI](#uso-via-cli)
- [Exemplos de uso](#exemplos-de-uso)
- [Saída esperada](#saída-esperada)
- [Estrutura do módulo](#estrutura-do-módulo)
- [Exemplo de saída por opção](#exemplo-de-saída-por-opção)

## Como funciona

Para cada execução, o `fix_video` percorre o diretório informado (ou o arquivo único) e, para cada vídeo encontrado, faz o seguinte:

1. **Lista os vídeos** (`support/video_list.py`) — busca recursivamente (`**/*.ext`) por arquivos com extensão `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`, `.m4v`, `.3gp`. Se `SOURCE` for um arquivo, processa apenas ele.
2. **Extrai informações com `ffprobe`** (`support/video_info.py`) — formato do container, streams, bit rate, tags de metadados, etc. Se o `ffprobe` não conseguir ler o arquivo (vídeo corrompido/truncado), as informações voltam vazias (`{}`).
3. **Verifica se já foi processado** — o arquivo é **pulado** (⏭️) se:
   - a tag de metadado `genre` já contém `Processed`/`Processado`/`Compressed`, ou
   - o nome do arquivo já termina em `.fix.mp4` ou `.fix.up.mp4`.
4. **Define o diretório de destino** (`library/library.py`) — mantém a mesma estrutura de subpastas relativa entre a origem e o destino (por padrão, origem e destino são o mesmo diretório).
5. **Executa o FFmpeg** (`support/video_fix.py`) de acordo com o `--mode` escolhido (veja abaixo), adicionando metadados customizados e salvando sempre como `.mp4`.
6. **Grava relatórios** em JSON Lines (um objeto JSON por linha) no diretório onde o comando foi executado.
7. **Remove o arquivo original**, a menos que `--no-remove` seja usado.

Ao final, é impresso um resumo com o total de arquivos processados e o tempo de execução.

## Modos de execução

Controlados pela opção `--mode` / `-m`:

### `up` (padrão) — acelerar e comprimir
Reencoda o vídeo aplicando aceleração de velocidade (vídeo `setpts` + áudio `atempo`) e um novo bit rate, além de padronizar o áudio para 44.1 kHz / 128k.
- Velocidade controlada por `--rate` / `-r` (padrão `1.75`).
- Bit rate de vídeo controlado por `--bit-rate` / `-br` (padrão `400` kbps).
- Sufixo do arquivo final: `.fix.up.mp4`.

### `compress` — apenas comprimir
Igual ao modo `up`, porém **sem** aplicar aceleração — só reencoda com o bit rate alvo.
- Sufixo do arquivo final: `.fix.comp.mp4`.

### `fix` — corrigir erros sem reencodar (ou recuperar vídeo truncado)
- Se o `ffprobe` conseguiu ler o arquivo: faz apenas um `stream copy` (`-c copy` com `-err_detect ignore_err`), sem reencodar — rápido e sem perda de qualidade.
- Se o `ffprobe` **não** conseguiu ler o arquivo (vídeo truncado/corrompido): usa o utilitário externo **`untrunc`** para reconstruir o vídeo a partir de um `--reference_file` / `-ref` (outro vídeo saudável gravado no mesmo aparelho/configuração), e em seguida reencoda o resultado com FFmpeg (`libx264` + `aac`).
- Sufixo do arquivo final: `.fix.mp4`.

## Convenção de nomes e metadados

Quando `--set-date` / `-sd` é informado (desativado por padrão), o nome do arquivo é normalizado por `library/fileinfo.py`:

- Procura uma data no próprio nome do arquivo (em português ou inglês). Se encontrar, usa essa data e remove o trecho correspondente do nome.
- Se não encontrar nenhuma data no nome, usa a data mais antiga entre criação/modificação/acesso do arquivo.
- Gera o novo nome no formato `AAAA.MM.DD - nome_original`.

Exemplo (com `-sd`): `IMG_1933.MOV` (criado em 11/09/2026) → `2026.09.11 - IMG_1933` + sufixo do modo + extensão. Sem `-sd`, o nome base é mantido como está (apenas removendo eventual `.fix` do nome).

Todo vídeo processado recebe metadados de controle via `-metadata` no FFmpeg (`library/library.py`), incluindo `genre` (usado para detectar arquivos já processados e evitar reprocessamento), `comment`, `description`, `copyright`, `year`, `date`, entre outros.

## Relatórios gerados

Todos os relatórios são arquivos **JSON Lines** (`.jsonl`-like: um JSON por linha) criados/atualizados no diretório atual (`ACTUAL_PATH`) a cada execução:

| Arquivo | Quando é gravado | Conteúdo |
|---|---|---|
| `__ffprobe_report.json` | Para cada vídeo antes de processar | Saída completa do `ffprobe` (streams, format, tags) |
| `__compress_report_ffmpeg.json` | Para cada vídeo processado com sucesso | Resumo do processamento (tamanhos antes/depois, tempo, comando executado) |
| `__error_report.json` | Quando um vídeo falha no processamento | `{"file": ..., "error": ...}` |

## Requisitos

- **FFmpeg** e **ffprobe** instalados e disponíveis no `PATH`.
- **untrunc** instalado e no `PATH` (necessário apenas para recuperar vídeos truncados no modo `fix`) — https://github.com/anthwlock/untrunc/releases
- Python `>= 3.14` com as dependências do projeto (`click`, `tqdm`, `dateparser`, ...).

## Uso via CLI

```bash
python -m src.main [SOURCE] [OPÇÕES]
```

| Opção | Atalho | Padrão | Descrição |
|---|---|---|---|
| `SOURCE` | — | `.` (diretório atual) | Arquivo ou diretório a processar |
| `--mode` | `-m` | `up` | Modo: `up`, `fix` ou `compress` |
| `--rate` | `-r` | `1.75` | Fator de aceleração usado no modo `up` |
| `--bit-rate` | `-br` | `400` | Bit rate alvo (kbps) para os modos `up`/`compress` |
| `--reference_file` | `-ref` | `None` | Vídeo de referência usado pelo `untrunc` no modo `fix` |
| `--no-remove` | `-nr` | desativado | Não remove o arquivo original após processar |
| `--set-date` | `-sd` | desativado | Normaliza o nome do arquivo com a data detectada |
| `--version` | — | — | Mostra a versão do `fix_video` |
| `--help` | — | — | Mostra a ajuda |

## Exemplos de uso

Acelerar e comprimir todos os vídeos do diretório atual (modo padrão `up`, 1.75x, 400 kbps):
```bash
python -m src.main
```

Processar um diretório específico, acelerando 2x com bit rate de 800 kbps:
```bash
python -m src.main C:/Users/fkfouri/Downloads -m up -r 2 -br 800
```

Apenas comprimir (sem acelerar) mantendo qualidade em 600 kbps:
```bash
python -m src.main C:/Users/fkfouri/Downloads -m compress -br 600
```

Corrigir erros de um vídeo sem reencodar, mantendo o arquivo original:
```bash
python -m src.main C:/Users/fkfouri/Downloads/video.mp4 -m fix -nr
```

Recuperar um vídeo truncado usando um vídeo de referência saudável:
```bash
python -m src.main C:/Users/fkfouri/Downloads/VID_20260911_corrompido.mp4 -m fix -ref C:/Users/fkfouri/Downloads/VID_20260910_ok.mp4
```

Acelerar e também renomear os arquivos com a data detectada (`-sd`):
```bash
python -m src.main C:/Users/fkfouri/Downloads -sd
```

## Saída esperada

### Console

```text
🚀🚀 Fix Video v1.0.9 🚀🚀
Started at 2026-09-11T10:15:32.123456
Running in mode: up at path: C:\Users\fkfouri\Downloads

 33%|███████████████                             | 1/3 [00:22<00:44, 22.1s/it]
⏭️ ⏭️  Skipping already processed file: C:\Users\fkfouri\Downloads\IMG_1900.fix.up.mp4 ⏭️ ⏭️

🟢🟢 fixed video:C:\Users\fkfouri\Downloads\IMG_1933.MOV, output: C:\Users\fkfouri\Downloads\IMG_1933.fix.up.mp4, exist_code: 0🟢🟢

100%|█████████████████████████████████████████████| 3/3 [00:51<00:00, 17.0s/it]

✅✅ All done! ✅✅
Total Files: 2
Finished at 2026-09-11T10:16:23.456789
Run from path: C:\Users\fkfouri\Downloads
```

- Arquivos já processados aparecem com `⏭️ ⏭️ Skipping already processed file`.
- Arquivos com erro aparecem com `❌❌ Error processing file ... ❌❌` e são gravados em `__error_report.json`, mas não interrompem o processamento dos demais.

### Arquivos gerados no diretório

Antes:
```
Downloads/
├── IMG_1933.MOV
└── IMG_1900.fix.up.mp4   (já processado)
```

Depois (modo `up`, sem `--no-remove`, sem `-sd`):
```
Downloads/
├── IMG_1933.fix.up.mp4
├── IMG_1900.fix.up.mp4
├── __ffprobe_report.json
└── __compress_report_ffmpeg.json
```

Com `-sd`, o resultado seria renomeado com a data detectada: `2026.09.11 - IMG_1933.fix.up.mp4`.

O arquivo original `IMG_1933.MOV` é removido (comportamento padrão); use `--no-remove` para mantê-lo.

### `__compress_report_ffmpeg.json` (uma linha por vídeo processado)

```json
{"original": "Downloads/IMG_1933.MOV", "original_size_mb": "185.32", "final": "Downloads/IMG_1933.fix.up.mp4", "final_size_mb": "62.10", "start_time": "2026-09-11T10:15:34.001000", "finish_time": "2026-09-11T10:16:12.900000", "processing_time": "00:38 (MM:SS)", "fix_type": "up", "speed_applied": "1.75x", "metadata_added": "yes", "cmd_executed": "ffmpeg -y -i C:\\Users\\fkfouri\\Downloads\\IMG_1933.MOV -b:v 400k -b:a 128k -ar 44100 -vf setpts=PTS/1.75 -af atempo=1.75 -metadata year=2026 ... C:\\Users\\fkfouri\\Downloads\\IMG_1933.fix.up.mp4"}
```

### `__error_report.json` (uma linha por erro)

```json
{"file": "C:\\Users\\fkfouri\\Downloads\\video_corrompido.mp4", "error": "..."}
```

## Estrutura do módulo

```
fix_video/
├── main.py                 # CLI (click) — ponto de entrada, laço principal
├── setup.py                # Constantes: paths de relatório, padrões de arquivo, metadados, flags
├── library/
│   ├── fileinfo.py          # Normalização de nome de arquivo com data (limpar_e_normalizar_nome_arquivo)
│   ├── library.py           # Metadados FFmpeg e cálculo do diretório de destino
│   └── report.py            # Escrita dos relatórios JSON Lines
└── support/
    ├── video_list.py         # Listagem dos vídeos na origem
    ├── video_info.py         # ffprobe + regra de "já processado"
    └── video_fix.py           # Montagem e execução dos comandos FFmpeg/untrunc por modo
```

## Exemplo de saída por opção

Comandos executados a partir de `C:\Users\fkfouri\Downloads`, contendo `IMG_1933.MOV` (185.32 MB, bit rate original ~2000 kbps).

### `SOURCE` (arquivo vs. diretório)

Diretório (processa todos os vídeos encontrados recursivamente):
```bash
python -m src.main C:/Users/fkfouri/Downloads
```
```text
Running in mode: up at path: C:\Users\fkfouri\Downloads
100%|████████████████████| 3/3 [00:58<00:00, 19.3s/it]
```

Arquivo único (processa apenas ele):
```bash
python -m src.main C:/Users/fkfouri/Downloads/IMG_1933.MOV
```
```text
Running in mode: up at path: C:\Users\fkfouri\Downloads\IMG_1933.MOV
100%|████████████████████| 1/1 [00:19<00:00, 19.3s/it]

🟢🟢 fixed video:C:\Users\fkfouri\Downloads\IMG_1933.MOV, output: C:\Users\fkfouri\Downloads\IMG_1933.fix.up.mp4, exist_code: 0🟢🟢
```

### `--mode up` / `-m up` (padrão)

```bash
python -m src.main -m up
```
```text
🟢🟢 fixed video:...\IMG_1933.MOV, output: ...\IMG_1933.fix.up.mp4, exist_code: 0🟢🟢
```
Gera `IMG_1933.fix.up.mp4`, com o vídeo acelerado (`setpts=PTS/1.75`, `atempo=1.75`) e metadado `genre=Processed - Acelerado 1.75× com FFmpeg (setpts + atempo)`.

### `--mode compress` / `-m compress`

```bash
python -m src.main -m compress
```
```text
🟢🟢 fixed video:...\IMG_1933.MOV, output: ...\IMG_1933.fix.comp.mp4, exist_code: 0🟢🟢
```
Gera `IMG_1933.fix.comp.mp4`, mesma duração do original, apenas com bit rate reduzido e metadado `genre=Processed - Compress from 2000k to 400k`.

### `--mode fix` / `-m fix`

Vídeo íntegro (o `ffprobe` conseguiu ler) — apenas `stream copy`, sem reencodar:
```bash
python -m src.main video.mp4 -m fix
```
```text
🟢🟢 fixed video:...\video.mp4, output: ...\video.fix.mp4, exist_code: 0🟢🟢
```

Vídeo truncado (o `ffprobe` falha) sem `--reference_file` — falha por falta de referência:
```bash
python -m src.main video_corrompido.mp4 -m fix
```
```text
❌❌ Error processing file C:\Users\fkfouri\Downloads\video_corrompido.mp4: ... ❌❌
```
(gravado em `__error_report.json`)

### `--rate` / `-r` (fator de aceleração, apenas no modo `up`)

```bash
python -m src.main -m up -r 2.5
```
```text
🟢🟢 fixed video:...\IMG_1933.MOV, output: ...\IMG_1933.fix.up.mp4, exist_code: 0🟢🟢
```
Comando FFmpeg gerado inclui `-vf setpts=PTS/2.5 -af atempo=2.5` e metadado `genre=Processed - Acelerado 2.5× com FFmpeg (setpts + atempo)`.

### `--bit-rate` / `-br` (bit rate alvo em kbps, modos `up`/`compress`)

```bash
python -m src.main -m compress -br 800
```
```text
🟢🟢 fixed video:...\IMG_1933.MOV, output: ...\IMG_1933.fix.comp.mp4, exist_code: 0🟢🟢
```
Comando FFmpeg gerado inclui `-b:v 800k`; no relatório: `"fix_type": "compress"`.

Valores `<= 1` são tratados como fração do bit rate original (ex.: `-br 0.5` → 50% do bit rate original do arquivo).

### `--reference_file` / `-ref` (usado com `-m fix` em vídeo truncado)

```bash
python -m src.main video_corrompido.mp4 -m fix -ref video_saudavel.mp4
```
```text
🟢🟢 fixed video:...\video_corrompido.mp4, output: ...\video_corrompido.fix.mp4, exist_code: 0🟢🟢
```
Internamente executa `untrunc video_saudavel.mp4 video_corrompido.mp4` seguido de um reencode com `ffmpeg -fflags +genpts ... -c:v libx264 -c:a aac`.

### `--no-remove` / `-nr`

```bash
python -m src.main -m up -nr
```
```text
🟢🟢 fixed video:...\IMG_1933.MOV, output: ...\IMG_1933.fix.up.mp4, exist_code: 0🟢🟢
```
Diferença: `IMG_1933.MOV` **permanece** no diretório após o processamento (sem essa flag, o original é removido).

### `--set-date` / `-sd`

Sem a flag (padrão):
```bash
python -m src.main -m up
```
```text
🟢🟢 fixed video:...\IMG_1933.MOV, output: ...\IMG_1933.fix.up.mp4, exist_code: 0🟢🟢
```

Com a flag:
```bash
python -m src.main -m up -sd
```
```text
🟢🟢 fixed video:...\IMG_1933.MOV, output: ...\2026.09.11 - IMG_1933.fix.up.mp4, exist_code: 0🟢🟢
```

### `--version`

```bash
python -m src.main --version
```
```text
fix_video, version 1.0.9
```

### `--help`

```bash
python -m src.main --help
```
```text
Usage: main.py [OPTIONS] [SOURCE]

  Fix and optimize video files using FFmpeg.

  SOURCE is the path to the file or directory to be processed.

Options:
  --version                      Show the version and exit.
  -ref, --reference_file PATH    Reference para untrunc
  -sd, --set-date                Set the date of the image.
  -m, --mode [up|fix|compress]   Choose the mode: up, fix or compress.
                                  Default is up.
  -nr, --no-remove                No allow removal of original files after
                                  processing.
  -r, --rate FLOAT               Valor de aceleração para o modo "up"
                                  (1.75x)
  -br, --bit-rate FLOAT           Taxa de bits alvo em kbps para o modo
                                  "compress" (400k)
  --help                          Show this message and exit.
```
