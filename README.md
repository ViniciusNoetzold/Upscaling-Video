# QualityScaler AI - Image & Video Upscaler

Aplicação web e desktop moderna para aumentar a resolução (upscale), restaurar texturas e remover ruídos de imagens e vídeos com Inteligência Artificial e processamento de alta precisão. Desenvolvido pela [Mezzold Studio](https://mezzoldstudio.com.br/).

---

## 🌐 Deploy no Render.com (Web Service)

O projeto está configurado para deploy automático em **1 clique** no [Render.com](https://render.com/):

1. Conecte o repositório no Render como **Web Service**.
2. O Render detectará automaticamente o Blueprint `render.yaml` ou `Procfile`:
   - **Runtime**: `Python`
   - **Python Version**: `3.11.8` (definido em `.python-version`)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
3. O serviço web fornece uma interface completa com drag & drop, seleção de fator (2x, 4x), remoção de ruídos e download dos resultados aprimorados.

---

## 🚀 Como Rodar Localmente

### Opção 1: Interface Web (Recomendado)
```bash
# 1. Instale as dependências
pip install -r requirements.txt

# 2. Inicie o servidor web
python run.py
```
Acesse `http://localhost:8000` no seu navegador.

### Opção 2: Interface Desktop (Windows)
```bash
python QualityScaler.py
```
Ou dê dois cliques em `Iniciar_QualityScaler.bat`.

---

## 🛠 Tecnologias e Bibliotecas

- **Python 3.11+**
- **FastAPI & Uvicorn** - Servidor web assíncrono de alta performance
- **ONNX Runtime** - Suporte a modelos neurais de super-resolução
- **OpenCV & Pillow** - Algoritmos de interpolação Lanczos, Unsharp Masking e Denoise
- **CustomTkinter** - Interface gráfica desktop alternativa (Windows)

---

## 🎯 Modelos e Modos de IA Suportados

- **BSRGAN** (BSRGANx2, BSRGANx4) - Restauração natural de fotos reais, rostos e vídeos comprimidos.
- **Real-ESRGAN** (RealESRGANx4, RealESR_Gx4) - Detalhes ultrafinos e nitidez para cenários e objetos.
- **RealESR Anime** (RealESR_Ax4) - Otimizado para animações e ilustrações 2D.
- **Clarity & Denoise** - Remoção de granulação e suavização inteligente de artefatos.

---

<p align="center">
  Desenvolvido com excelência pela <a href="https://mezzoldstudio.com.br/"><strong>Mezzold Studio</strong></a><br>
  <em>Software House Premium • Micro SaaS & Dashboards de Alta Performance</em>
</p>

