# Fix Video

Identificado que os videos ficam ruim depois de baixar via CocoCut.

Baseado no codigo https://gist.github.com/masgari/2ba5f8fb19a735ffbf066022090ae128

RODAR EM WINDOWS para gerar .EXE

## Rodar como pacote
``` bash
python -m src.main
python -m src.main --help
```

## Setup
```
uv self update

uv sync --no-cache --native-tls


uv python list

python 
```

## Instalar o ffmpeg

```bash

sudo apt install ffmpeg -y

ffmpeg -version
```

## Instalar o untrunc
https://github.com/anthwlock/untrunc/releases


Referencia futura
```bash
# quero passar um video mp4 de 30 para 24 frames por segundo, tonar o audio sample de 48 para 44.100 Khz usando o ffmpeg

ffmpeg -i input.mp4 -r 24 -ar 44100 output.mp4

# Explicação dos parâmetros:
# -i input.mp4 → Especifica o vídeo de entrada.
# -r 24 → Ajusta a taxa de frames para 24 FPS.
# -ar 44100 → Converte o áudio para 44.1 kHz.
# output.mp4 → Nome do arquivo de saída.
```

🚀 Se quiser manter a melhor qualidade possível:
Caso da filmagem seep
```bash
ffmpeg -i input.mp4 -r 24 -ar 44100 -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k output.mp4


ffmpeg -y -i C:/Users/fkfouri/Downloads/IMG_1933.mp4 -r 24 -b:v 400k -b:a 128k -ar 44100  C:/dev/fix_video/origem//_A_IMG_1933.fix.up.mp4


ffmpeg -y -i C:/Users/fkfouri/Downloads/IMG_1933.MOV -c:v libx264 -crf  23 -preset medium -c:a aac -b:a 128k -vf format=yuv420p C:/dev/fix_video/origem/IMG_1933.fix.up.mp4

ffmpeg -y -i C:/Users/fkfouri/Downloads/IMG_1933.MOV -qscale 0 C:/dev/fix_video/origem/IMG_1933.fix.up.mp4  

ffmpeg -y -i C:/Users/fkfouri/Downloads/IMG_1933.MOV  -q:v 0 -q:a 0 C:/dev/fix_video/origem/IMG_1933.fix.up.mp4  

# Tipo copio... sei la
# Lossless Conversion (if codecs are compatible):
ffmpeg -y -i C:/Users/fkfouri/Downloads/IMG_1933.MOV -c:v copy -c:a copy C:/dev/fix_video/origem/IMG_1933.mp4  

# High-Quality Re-encoding:
ffmpeg -y -i C:/Users/fkfouri/Downloads/IMG_1933.MOV -c:v libx264 -crf 18 -c:a aac -b:a 128K C:/dev/fix_video/origem/IMG_1933.fix.up.mp4  


ffmpeg -y -err_detect ignore_err -i VID_20211211_181906.mp4 -c copy  VID_20211211_181906.fix.mp4
```