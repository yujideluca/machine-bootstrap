---
name: "reparo-kubuntu"
description: "Diagnostica e corrige problemas do notebook Acer Nitro do Giovanni (Kubuntu 24.04, Plasma 5.27, X11, Nvidia) e torna as correções permanentes entre reinicializações."
---

# Reparo Kubuntu

Interop: role = domain; owns = fluxo de diagnóstico/correção no Linux dele; defers to = browser-automacao-segura (se usar navegador); honors = idioma da mensagem, flags !! *** ...

Método (Google SRE "Effective Troubleshooting" 2016; Ubuntu Seven-Step Troubleshooting): estabilizar e preservar evidência → examinar → hipóteses ordenadas por probabilidade → **uma mudança por vez** → corrigir → retestar após reboot → documentar. Armadilhas: perseguir sintoma irrelevante, mudança insegura durante o teste, assumir que a causa antiga voltou.

## 0. Formato
Conclusão primeiro: hipótese principal + o próximo passo. `!!` → até 5 linhas: hipótese, 1 teste, 1 correção, como verificar. Toda resposta que propõe correção termina com **Verificar** (o que checar após reiniciar) e **Desfazer** (como reverter).

## 1. Estabilizar e coletar (sem mudar nada)
Se o computador dele estiver ligado à sessão, rode você mesmo; senão, um bloco para colar:
```bash
{ lsb_release -ds; uname -r; plasmashell --version; echo "session=$XDG_SESSION_TYPE";
  nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null;
  journalctl --user -b -p warning --no-pager | tail -60; journalctl -b -p err --no-pager | tail -40;
  coredumpctl list --since=-2d --no-pager | tail -10; ls -lt /var/log/apt/history.log* | head -2; tail -30 /var/log/apt/history.log; } > ~/diag_$(date +%F_%H%M).txt 2>&1; echo salvo
```
Pergunte só o que o log não responde: o que mudou (update, config, tema) e se é reproduzível.

## 2. Mapa de sintomas → primeira hipótese (do histórico dele)
| Sintoma | Hipótese 1 | Teste seguro |
|---|---|---|
| tela preta / sem painel / plasmashell ou krunner cai | crash do plasmashell (fontconfig `FcCharSetHasChar`, tema ausente) | `coredumpctl info plasmashell`; `systemctl --user restart plasma-plasmashell` |
| crash em libfontconfig | cache de fontes corrompido / fonte web (woff) mal casada | `fc-cache -r -v`; `fc-match sans` |
| letras acentuadas maiúsculas / teclado estranho | Fcitx + layout/modelo (`pc104alt`, `br`) | `fcitx5-diagnose`; `setxkbmap -query` |
| touchpad sem configuração | módulo/driver (libinput × synaptics, receptor XCTECH) | `xinput list`; `journalctl -k \| grep -i touch` |
| boot lento | `NetworkManager-wait-online`, fstab | `systemd-analyze blame \| head`; `systemd-analyze critical-chain` |
| flicker / tela | driver Nvidia × kernel | `ubuntu-drivers devices`; `dkms status` |

## 3. Mudar com segurança
- Uma mudança por vez; diga o que ela prova.
- Antes de editar: backup com data (`cp -a`). Nunca `rm -rf` em `~/.config` ou `/etc`: mova para quarentena. Antes de mexer em driver/kernel: snapshot (Timeshift) se disponível.
- Comandos com `sudo` explicados em uma linha.

## 4. Tornar permanente (prioridade dele)
- Correção vira `~/fixes/<nome>.sh` (idempotente, com checagem final).
- Precisa rodar a cada sessão → unit systemd do usuário `~/.config/systemd/user/<nome>.service` (`Type=oneshot`, `After=graphical-session.target` e, se mexer no Plasma, `After=plasma-plasmashell.service`, `ExecStart=%h/fixes/<nome>.sh`, `WantedBy=graphical-session.target`) + `systemctl --user enable <nome>`.
- Variável de ambiente do Plasma → `~/.config/plasma-workspace/env/`.

## 5. Retestar e registrar
Reiniciar, rodar o bloco do passo 1, comparar com o anterior. Registre causa, correção e como desfazer em `~/fixes/LEIAME.md`.