# Contador en Logisim hasta 5 minutos (MM:SS) con parada manual

Este diseño cuenta desde **00:00** hasta **05:00** y también puede detenerse cuando tú lo indiques con un botón (`STOP`).

---

## 1) Idea general del circuito

Vamos a dividir el tiempo en 4 dígitos BCD:

- `U_s`: unidades de segundo (0–9)
- `D_s`: decenas de segundo (0–5)
- `U_m`: unidades de minuto (0–5)
- `D_m`: decenas de minuto (si quieres exactamente 5:00, este puede quedar fijo en 0)

Para el requisito “máximo cinco minutos”, realmente basta con:
- Minutos: `0..5`
- Segundos: `00..59`

Cuando llegue a **05:00**, se deshabilita el conteo automáticamente.

---

## 2) Bloques que necesitas en Logisim

1. **Clock** (1 Hz recomendado).
2. **4 contadores BCD** (o contadores binarios + lógica de reset a 10/6 según dígito).
3. **Comparadores** (para detectar 9, 5, 59 y 5:00).
4. **Compuertas AND/OR/NOT** para señales de acarreo y habilitación.
5. **4 displays de 7 segmentos** (o 2 si agrupas minutos y segundos con decodificador).
6. **Botones**:
   - `START`
   - `STOP`
   - `RESET`
7. **Flip-flop SR o D** para mantener estado de marcha (`RUN`).

---

## 3) Señal de ejecución (RUN)

Crea una memoria de estado para que el contador siga corriendo aunque sueltes el botón.

- `START` pone `RUN = 1`
- `STOP` pone `RUN = 0`
- `RESET` pone todo a 0 y `RUN = 0`

Ecuación de habilitación global:

```text
ENABLE_GLOBAL = RUN AND (NOT LIMIT_5MIN)
```

Donde `LIMIT_5MIN = 1` cuando el tiempo sea exactamente 05:00.

---

## 4) Lógica de cada dígito

## 4.1 Unidades de segundo (`U_s`: 0..9)

- Incrementa con cada pulso de reloj de 1 Hz si `ENABLE_GLOBAL = 1`.
- Cuando llega a 9 y entra un pulso, vuelve a 0 y genera acarreo a `D_s`.

```text
CARRY_Us = ENABLE_GLOBAL AND (U_s == 9)
```

## 4.2 Decenas de segundo (`D_s`: 0..5)

- Incrementa con `CARRY_Us`.
- Cuando llega a 5 y recibe acarreo, vuelve a 0 y genera acarreo a `U_m`.

```text
CARRY_Ds = CARRY_Us AND (D_s == 5)
```

## 4.3 Unidades de minuto (`U_m`: 0..5)

- Incrementa con `CARRY_Ds`.
- Para este problema solo necesitamos hasta 5.

```text
CARRY_Um = CARRY_Ds AND (U_m == 5)
```

> En este diseño, no necesitas que siga a decenas de minuto porque el tope es 5:00.

---

## 5) Detección de límite en 5:00

Define:

```text
LIMIT_5MIN = (U_m == 5) AND (D_s == 0) AND (U_s == 0)
```

Si usas `D_m`, añade también `(D_m == 0)`.

Al activarse `LIMIT_5MIN`, `ENABLE_GLOBAL` pasa a 0 y el circuito se queda congelado en **05:00**.

---

## 6) Diagrama lógico (vista rápida)

```text
         START ----\
                     >--- [RUN LATCH] ---- RUN ----\
          STOP -----/                            AND ---- ENABLE_GLOBAL ---> contadores
                                                   / \
                                LIMIT_5MIN --NOT--/   \

Clock 1Hz ----------------------------------------------> U_s (0..9)
                                U_s==9 ---------------> carry --> D_s (0..5)
                                D_s==5 + carry -------> carry --> U_m (0..5)

LIMIT_5MIN = (U_m==5) AND (D_s==0) AND (U_s==0)
```

---

## 7) Paso a paso para construirlo en Logisim

1. **Coloca el Clock** y pon frecuencia de simulación a 1 Hz (o divide reloj si hace falta).
2. **Añade latch RUN**:
   - Opción fácil: flip-flop D con realimentación y lógica de set/reset.
   - Entradas: `START`, `STOP`, `RESET`.
3. **Añade contador `U_s`**:
   - Configurado módulo 10.
   - `Enable = ENABLE_GLOBAL`.
4. **Añade comparador `U_s == 9`** y genera `CARRY_Us`.
5. **Añade contador `D_s`** módulo 6:
   - `Enable = CARRY_Us`.
6. **Comparador `D_s == 5`** y genera `CARRY_Ds`.
7. **Añade contador `U_m`** módulo 6:
   - `Enable = CARRY_Ds`.
8. **Comparadores para límite**:
   - `U_m == 5`
   - `D_s == 0`
   - `U_s == 0`
   - AND de los tres = `LIMIT_5MIN`.
9. **Genera `ENABLE_GLOBAL`** con `RUN AND NOT(LIMIT_5MIN)`.
10. **Conecta a displays** (cada dígito a su 7-seg con decodificador BCD).
11. **Prueba**:
    - `RESET` → 00:00
    - `START` → comienza a contar
    - `STOP` → se pausa
    - `START` → continúa
    - Verifica paro automático en 05:00.

---

## 8) Comprobación rápida (tabla de estados clave)

| Tiempo | LIMIT_5MIN | ENABLE_GLOBAL (si RUN=1) | Acción |
|---|---:|---:|---|
| 04:59 | 0 | 1 | Siguiente pulso -> 05:00 |
| 05:00 | 1 | 0 | Se detiene |
| 05:00 + START | 1 | 0 | Sigue detenido |
| RESET | 0 | 0 | Vuelve a 00:00 |

---

## 9) Si quieres “parar donde uno le diga”

Ya está incluido con `STOP`. Si quieres reanudar, usa `START`.
Si quieres “ir a un tiempo específico”, agrega switches de carga paralela en los contadores y una señal `LOAD`.

