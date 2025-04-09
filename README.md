# 🎮 Kodland Survivals

![banner](https://user-images.githubusercontent.com/0000000/banner-placeholder.png)

Um jogo de sobrevivência no estilo *roguelike* feito com 💻 **Python + PGZero**, onde você enfrenta ondas de inimigos, desbloqueia upgrades e tenta sobreviver o máximo possível!

---

## ✨ Sobre o Projeto

Kodland Survivals é um jogo desenvolvido como parte de um desafio para tutores da Kodland, utilizando Python com a biblioteca **PGZero** (baseada em Pygame).

Você controla um personagem usando `WASD`, mira com o mouse e atira com o clique. A cada nova onda de inimigos eliminada, você pode **escolher entre diferentes upgrades** para melhorar suas habilidades.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.9**
- **PGZero (Pygame Zero)**
- **Pygame**
- **Visual Studio Code**
- **Photoshop** (edição de assets)
- **Kenney.nl** (sprites e sons)
- **Freesound.org** (efeitos sonoros adicionais)

---

## 🎮 Controles

| Tecla / Ação        | Função                              |
|---------------------|-------------------------------------|
| `W`, `A`, `S`, `D`  | Movimentação                        |
| Mouse               | Mira                                |
| Clique do mouse     | Atira                               |
| `ESC`               | Volta para o menu principal         |
| `R`                 | Reinicia o jogo após a morte        |
| Botão do menu       | Pausa/despausa a música             |

---

## 💡 Sistema de Upgrades

A cada onda completada, você escolhe **1 entre 5 upgrades aleatórios** que melhoram seu personagem:

### 🛡️ Tipos de upgrades disponíveis:
- **Aumentar Dano (+5)**
- **Aumentar Vida (+20)**
- **Aumentar Velocidade (+20%)**
- **Aumentar Cadência (+25%)**
- **Vampirismo (10% de vida a cada inimigo derrotado)**

Esses upgrades tornam cada partida única e trazem um elemento estratégico ao jogo.

---

## 🧠 Como Rodar o Projeto

1. Certifique-se de ter o **Python 3.9+** instalado.
2. Instale a biblioteca PGZero:
   ```bash
   pip install pgzero
