import cv2
import imutils

def pre_processar_imagem(imagem):
    gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)
    
    edged = cv2.Canny(gray, 50, 100)
    
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    
    if len(cnts) == 0:
        return None
    
    c = max(cnts, key=cv2.contourArea)
    
    (x, y, w, h) = cv2.boundingRect(c)
    
    imagem_processada = imagem[y:y+h, x:x+w]
    
    imagem_processada = cv2.resize(imagem_processada, (200, 200))

    return imagem_processada

def identificar_sinal(frame, pedra, papel, tesoura):
    
    p_frame = pre_processar_imagem(frame)
    p_pedra = pre_processar_imagem(pedra)
    p_papel = pre_processar_imagem(papel)
    p_tesoura = pre_processar_imagem(tesoura)

    try:
        d_pedra = cv2.absdiff(p_frame, p_pedra).mean()
        d_papel = cv2.absdiff(p_frame, p_papel).mean()
        d_tesoura = cv2.absdiff(p_frame, p_tesoura).mean()
    except cv2.error:
        return None
    
    if d_pedra < d_papel and d_pedra < d_tesoura:
        return 'pedra'
    elif d_papel < d_pedra and d_papel < d_tesoura:
        return 'papel'
    elif d_tesoura < d_pedra and d_tesoura < d_papel:
        return 'tesoura'
    else:
        return None


cap = cv2.VideoCapture('./assets/pedra-papel-tesoura.mp4')

pedra = cv2.imread('./assets/pedra.jpeg')
papel = cv2.imread('./assets/papel.jpeg')
tesoura = cv2.imread('./assets/tesoura.jpeg')

vitorias_esquerda = 0
vitorias_direita = 0

sinal_esquerda_anterior = None
sinal_direita_anterior = None

while True:
    ret, frame = cap.read()
    
    if not ret:
        break

    (h, w) = frame.shape[:2]
    meio = w // 2
    esquerda = frame[:, :meio]
    direita = frame[:, meio:]

    sinal_esquerda = identificar_sinal(esquerda, pedra, papel, tesoura)

    pedra_espelhada = cv2.flip(pedra, 1)
    papel_espelhada = cv2.flip(papel, 1)
    tesoura_espelhada = cv2.flip(tesoura, 1)
    
    sinal_direita = identificar_sinal(direita, pedra_espelhada, papel_espelhada, tesoura_espelhada)

    cv2.putText(frame, "Jogador 1: " + sinal_esquerda, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    text_size, _ = cv2.getTextSize("Jogador 2: " + sinal_direita, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    text_x = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) - text_size[0] - 10)
    cv2.putText(frame, "Jogador 2: " + sinal_direita, (text_x, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    if sinal_esquerda is not None and sinal_direita is not None:
        if sinal_esquerda == 'pedra':
            if sinal_direita == 'pedra':
                resultado = 'empate'
            elif sinal_direita == 'papel':
                resultado = 'jogador 2 ganhou'
            elif sinal_direita == 'tesoura':
                resultado = 'jogador 1 ganhou'
        elif sinal_esquerda == 'papel':
            if sinal_direita == 'pedra':
                resultado = 'jogador 1 ganhou'
            elif sinal_direita == 'papel':
                resultado = 'empate'
            elif sinal_direita == 'tesoura':
                resultado = 'jogador 2 ganhou'
        elif sinal_esquerda == 'tesoura':
            if sinal_direita == 'pedra':
                resultado = 'jogador 2 ganhou'
            elif sinal_direita == 'papel':
                resultado = 'jogador 1 ganhou'
            elif sinal_direita == 'tesoura':
                resultado = 'empate'
    else:
        resultado = None

    if resultado is not None:
        text_size, _ = cv2.getTextSize(resultado, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        text_x = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) / 2 - text_size[0] / 2)
        cv2.putText(frame, resultado, (text_x, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    if resultado is not None and sinal_esquerda != sinal_esquerda_anterior or sinal_direita != sinal_direita_anterior:
        sinal_esquerda_anterior = sinal_esquerda
        sinal_direita_anterior = sinal_direita

        if resultado == 'jogador 1 ganhou':
            vitorias_esquerda += 1
        
        if resultado == 'jogador 2 ganhou':
            vitorias_direita += 1

    final_da_tela = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) - 10)
    cv2.putText(frame, "vitorias jogador 1: " + str(vitorias_esquerda), (50, final_da_tela - 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(frame, "vitorias jogador 2: " + str(vitorias_direita), (50, final_da_tela - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow('Jokenpo', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
