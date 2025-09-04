# 🏀 Basket Beta

Basket Beta é um jogo 2D simples de basquete desenvolvido em **Python** com **Pygame**, criado inicialmente como parte de um trabalho da faculdade.  
O objetivo é acertar a cesta controlando o arremesso por meio de uma barra de força dinâmica.  

---

## 🎮 Gameplay

- O jogador inicia com **3 tentativas**.  
- Uma **barra de força oscilante** define a precisão do arremesso:  
  - 🟢 **Verde** → acerto garantido  
  - 🟡 **Amarelo** → resultado incerto (pode ser quase ou acerto)  
  - 🔴 **Vermelho** → erro  
- Cada erro reduz as tentativas em **-1**.  
- O jogo termina ao zerar as tentativas.  
- Sprites customizados representam o jogador, a bola e a cesta em diferentes estados (idle, arremesso, acerto, erro).  
- A bola segue uma **animação em arco** até o alvo, variando conforme a zona da barra.  

---

## 🖼️ Screenshots

![Vídeo Demo](https://github.com/user-attachments/assets/1288c64e-0892-4d26-8346-b99a51dce9a3)


---

## ⚙️ Tecnologias utilizadas

- **Python 3**  
- **Pygame** (renderização 2D, sprites, animações)  
- **PyInstaller** (empacotamento do jogo em executável)  

---
   git clone https://github.com/SEU-USUARIO/basket-beta.git
   cd basket-beta
