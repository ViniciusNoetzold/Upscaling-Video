# QualityScaler - AI Image & Video Upscaler

QualityScaler é uma aplicação para Windows desenvolvida em Python que utiliza Inteligência Artificial para aumentar a resolução (upscale), aprimorar e remover ruídos de imagens e vídeos com aceleração por GPU.

---

## 🚀 Guia Rápido: Como Configurar e Rodar em Outro PC

Siga este passo a passo para colocar o projeto funcionando em qualquer computador com Windows:

### 1. Clonar o Repositório
Abra o PowerShell ou Terminal e execute:
`powershell
git clone https://github.com/ViniciusNoetzold/Upscaling-Video.git
cd Upscaling-Video
`

---

### 2. Criar o Ambiente Virtual e Instalar Dependências (Apenas 1ª vez)
`powershell
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
`

---

### 3. Colocar os Arquivos Pesados (Não inclusos no Git)

1. **Modelos de IA (.onnx)**:
   - Baixe ou copie os modelos .onnx para dentro da pasta AI-onnx/.
   - *Principais modelos recomendados:* BSRGANx2_fp16.onnx, RealESRGANx4_fp16.onnx, RealESR_Gx4_fp16.onnx.
   - *Download alternativo:* Podem ser obtidos no Hugging Face (svjack/AI-onnx) ou na seção de Releases.

2. **FFmpeg (fmpeg.exe)**:
   - Copie o arquivo fmpeg.exe (com suporte a NVENC/CUDA) para dentro da pasta Assets/.
   - *Download alternativo:* [Gyan.dev FFmpeg Release Essentials](https://www.gyan.dev/ffmpeg/builds/) (extrair fmpeg.exe para Assets/).

---

### 4. Executar a Aplicação

Dê dois cliques no arquivo:
👉 **Iniciar_QualityScaler.bat**

Ou rode pelo terminal:
`powershell
.\venv\Scripts\python.exe QualityScaler.py
`

---

## 📦 Releases / Executável Standalone

Você também pode baixar a versão empacotada diretamente na aba de **Releases** do repositório.

---

## 🛠 Tecnologias e Bibliotecas

- **Python 3.11+**
- **ONNX Runtime (DirectML)** - Suporte a GPUs DirectX 12 (NVIDIA / AMD / Intel)
- **CustomTkinter** - Interface gráfica moderna
- **OpenCV & Pillow** - Manipulação e processamento de imagem
- **FFmpeg** - Extração de frames e codificação acelerada por hardware (NVENC, QSV, AMF)

---

## 🎯 Modelos Suportados

- **BSRGAN** (BSRGANx2, BSRGANx4) - Excelente para restauração natural de vídeos reais, rostos e remoção de compressão.
- **Real-ESRGAN** (RealESRGANx4, RealESR_Gx4) - Detalhes e nitidez aprimorados.
- **RealESR Anime** (RealESR_Ax4) - Otimizado para animações e ilustrações 2D.
- **LVA** (LVAx2) - Modelo ultra rápido e leve para vídeos longos.
- **IRCNN** (IRCNN_Mx1, IRCNN_Lx1) - Denoise e remoção de ruídos em 1x.
