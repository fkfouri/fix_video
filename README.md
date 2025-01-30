# Fix Video

Identificado que os videos ficam ruim depois de baixar via  CocoCut.

Baseado no codigo https://gist.github.com/masgari/2ba5f8fb19a735ffbf066022090ae128


```bash

sudo apt install ffmpeg -y

ffmpeg -version
```

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
```bash
ffmpeg -i input.mp4 -r 24 -ar 44100 -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k output.mp4

# -c:v libx264 → Usa o codec H.264 para compressão eficiente.
# -preset slow → Mantém boa qualidade de compressão.
# -crf 18 → Controla a qualidade do vídeo (menor = melhor).
-c:a aac -b:a 192k → Usa AAC para áudio e define o bitrate para 192 kbps.
```