import av
import cv2
import time
import numpy as np
import onnxruntime as ort
import pyautogui
import os
from dotenv import load_dotenv
load_dotenv()



# --- CONFIGURAÇÕES DE INTERFACE ---
pyautogui.PAUSE = 0.02
COORDS = {
    'esquerda': (330, 975),
    'direita': (385, 975),
    'cima': (356, 947),
    'baixo': (356, 1005)
}

# --- CONFIGURAÇÕES DE RASTREAMENTO ---
ZONA_X_MIN, ZONA_X_MAX = 0.2, 0.7  
ZONA_Y_MIN, ZONA_Y_MAX = 0.2, 0.8  
COOLDOWN_MOVIMENTO = 0.5           

# Limites de Confiança (Reduzido para cachorros devido ao ângulo)
CONF_PESSOA = 0.5
CONF_CACHORRO = 0.3

URL_RTSP = os.getenv('URL_CAM')
MODELO_ONNX = "yolov8x.onnx"

print(f"Conectando via PyAV e carregando GPU...")
sessao = ort.InferenceSession(MODELO_ONNX, providers=['DmlExecutionProvider'])
nome_entrada_onnx = sessao.get_inputs()[0].name

ultimo_movimento = 0

def mover_camera(direcoes):
    for d in direcoes:
        if d:
            x, y = COORDS[d]
            pyautogui.moveTo(x, y)
            pyautogui.mouseDown()
            time.sleep(0.05) 
            pyautogui.mouseUp()

while True:
    try:
        container = av.open(URL_RTSP)
        print("Câmera online.")
        
        for pacote in container.demux():
            if pacote.stream.type == 'video':
                for frame_bruto in pacote.decode():
                    img = frame_bruto.to_ndarray(format='bgr24')
                    h_img, w_img = img.shape[:2]
                    tempo_atual = time.time()

                    # IA Processamento (YOLOv8)
                    img_input = cv2.resize(img, (640, 640))
                    img_input = cv2.cvtColor(img_input, cv2.COLOR_BGR2RGB)
                    img_input = np.transpose(img_input, (2, 0, 1)).astype(np.float32) / 255.0
                    img_input = np.expand_dims(img_input, axis=0)
                    
                    saidas = sessao.run(None, {nome_entrada_onnx: img_input})[0]
                    saidas = np.squeeze(saidas)
                    
                    conf_pessoas = saidas[4, :]
                    conf_caes = saidas[20, :]
                    
                    # Filtra usando os limites individuais
                    idx_validos = np.where((conf_pessoas > CONF_PESSOA) | (conf_caes > CONF_CACHORRO))[0]

                    direcoes_para_mover = []
                    alvo_detectado = False

                    if len(idx_validos) > 0:
                        bboxes_nms, scores_nms, classes_nms = [], [], []
                        escala_x, escala_y = w_img / 640.0, h_img / 640.0
                        
                        for idx in idx_validos:
                            cp, cc = conf_pessoas[idx], conf_caes[idx]
                            x, y, w, h = saidas[:4, idx]
                            box = [int((x-w/2)*escala_x), int((y-h/2)*escala_y), int(w*escala_x), int(h*escala_y)]
                            
                            if cp > CONF_PESSOA and cp >= cc:
                                bboxes_nms.append(box)
                                scores_nms.append(float(cp))
                                classes_nms.append("Pessoa")
                            elif cc > CONF_CACHORRO and cc > cp:
                                bboxes_nms.append(box)
                                scores_nms.append(float(cc))
                                classes_nms.append("Cachorro")
                                
                        # NMS Threshold ajustado para 0.3 para evitar que caixas se sobreponham e sumam
                        indices = cv2.dnn.NMSBoxes(bboxes_nms, scores_nms, 0.3, 0.4)
                        
                        if len(indices) > 0:
                            melhor_i = indices.flatten()[0] # O primeiro é o de maior confiança
                            
                            # Desenha todos os alvos detectados
                            for i in indices.flatten():
                                bx, by, bw, bh = bboxes_nms[i]
                                classe_alvo = classes_nms[i]
                                score_alvo = scores_nms[i]
                                
                                cx = bx + bw // 2
                                
                                if classe_alvo == "Pessoa":
                                    cy = by + int(bh * 0.15) 
                                    cor = (0, 255, 0)
                                else:
                                    cy = by + bh // 2 
                                    cor = (255, 165, 0)
                                    
                                # Quadrado, bolinha de mira e texto de porcentagem
                                cv2.rectangle(img, (bx, by), (bx+bw, by+bh), cor, 2)
                                cv2.circle(img, (cx, cy), 8, (0, 0, 255), -1)
                                texto = f"{classe_alvo} {int(score_alvo * 100)}%"
                                cv2.putText(img, texto, (bx, by - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, cor, 2)

                                # Rastrea apenas o alvo de maior confiança
                                if i == melhor_i:
                                    alvo_detectado = True
                                    if cx < w_img * ZONA_X_MIN: direcoes_para_mover.append('esquerda')
                                    elif cx > w_img * ZONA_X_MAX: direcoes_para_mover.append('direita')

                                    if cy < h_img * ZONA_Y_MIN: direcoes_para_mover.append('cima')
                                    elif cy > h_img * ZONA_Y_MAX: direcoes_para_mover.append('baixo')

                    if alvo_detectado and direcoes_para_mover and (tempo_atual - ultimo_movimento > COOLDOWN_MOVIMENTO):
                        mover_camera(direcoes_para_mover)
                        ultimo_movimento = tempo_atual

                    # Desenha a zona morta (Retângulo de referência amarelo)
                    cv2.rectangle(img, (int(w_img*ZONA_X_MIN), int(h_img*ZONA_Y_MIN)), 
                                  (int(w_img*ZONA_X_MAX), int(h_img*ZONA_Y_MAX)), (0, 255, 255), 2)
                    
                    cv2.imshow("Tracking 2D (Multi-Alvos)", cv2.resize(img, (1024, 576)))
                    if cv2.waitKey(1) & 0xFF == ord('q'): exit()

    except Exception as e:
        print(f"Erro na transmissão: {e}. Reconectando...")
        time.sleep(2)