# Tracking Surveillance for Yoosee

Este projeto implementa um sistema de auto-tracking (acompanhamento inteligente) utilizando visão computacional (YOLOv8) para detectar, focar e centralizar pessoas e animais.

**⚠️ IMPORTANTE: Arquitetura e Compatibilidade**
* **Exclusivo para GPUs AMD:** Este código foi pensado e otimizado inteiramente para rodar em placas de vídeo da AMD (via DirectML). Essa arquitetura foi escolhida para contornar a burocracia de configuração e incompatibilidades frequentes de outros frameworks.
* **Exclusivo para Yoosee:** A lógica de movimentação, tempo de clique e limites de área foi desenhada exclusivamente para interagir com o software de controle das câmeras Yoosee.

## Estrutura de Arquivos

* `tracker_camera.py`: Script principal responsável por conectar ao feed de vídeo, rodar a inferência da IA e enviar os comandos físicos de clique para ajustar a câmera.
* `coordinates.py`: Script utilitário em pop-up transparente. **Ele serve única e exclusivamente para mapear as coordenadas (X, Y)** dos botões direcionais do aplicativo Yoosee na sua tela, dados que devem ser inseridos no script principal.

## Instalação e Dependências

Para que a execução na GPU AMD e as automações funcionem corretamente, instale os pacotes abaixo. Bibliotecas como `os`, `time` e `tkinter` já são nativas do Python.

```bash
pip install av opencv-python "numpy<2" onnxruntime-directml pyautogui python-dotenv
```

> **💡 RESOLUÇÃO DE PROBLEMAS (AMD + ONNX):**
> O pacote `onnxruntime-directml` pode apresentar conflitos de compatibilidade com versões do NumPy iguais ou superiores a 2.0. Caso você tenha instalado as bibliotecas separadamente e o script apresente erro ao carregar o modelo na GPU, force o downgrade do NumPy rodando explicitamente o comando: `pip install "numpy<2"`.

## Modelo YOLOv8 e `.gitignore`

Devido aos limites de tamanho de arquivo do GitHub, o modelo da inteligência artificial não está incluso neste repositório. 

1. Baixe ou exporte o modelo **YOLOv8x** no formato ONNX (`yolov8x.onnx`).
2. Coloque o arquivo na raiz do projeto, na mesma pasta do script principal.

## Configuração de Ambiente (.env)

Por segurança, a URL da câmera não fica exposta no código. Crie um arquivo `.env` na mesma pasta dos scripts e defina a sua rota de conexão usando a variável `URL_CAM` (que será lida internamente como `URL_RTSP` pelo sistema).

Conteúdo do seu arquivo `.env`:
```env
URL_CAM="rtsp://admin:senha@192.168.X.X:554/onvif1"
```

---

> **📌 OBSERVAÇÃO: ROADMAP E MUDANÇA DE ROTAS**
> 
> Futuramente, a captação de vídeo via protocolo RTSP será totalmente abandonada neste projeto. A nova abordagem consistirá em capturar e espelhar a tela do próprio aplicativo desktop do Yoosee para que o código "enxergue" a imagem nativa. Essa decisão foi tomada porque as câmeras Yoosee possuem um ecossistema extremamente burocrático, fechado e instável para conexões externas, o que dificulta e limita a criação e manutenção de códigos diretos via rede.
