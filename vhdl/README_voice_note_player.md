# Diseño modular: Reproductor de nota de voz (VHDL)

## 1) Explicación del diseño

El sistema se divide en 4 bloques lógicos:

1. **Entrada y validación de tiempo**
   - Recibe `target_min`, `target_sec_t`, `target_sec_u`.
   - Valida que el tiempo esté en el rango `0:00` a `5:00`.

2. **Generador de tick con velocidad**
   - Desde `clk` del sistema se genera `sec_tick`.
   - `1x`: tick cada 1 segundo.
   - `2x`: tick cada 0.5 segundos.
   - `1.5x`: patrón alternado para lograr promedio de 1.5 segundos reproducidos por segundo real.

3. **Control de reproducción + contador BCD (MM:SS)**
   - Al presionar `start`, si el tiempo es válido, inicia en `0:00`.
   - Cuenta ascendente hasta el tiempo objetivo.
   - Al finalizar activa `done_led`.

4. **Salidas de visualización**
   - Expone `cur_min`, `cur_sec_t`, `cur_sec_u` para displays.
   - Señales one-hot `speed_1x`, `speed_1_5x`, `speed_2x` para indicadores de velocidad.

---

## 2) Diagrama de bloques (texto)

```text
                +--------------------------+
clk, rst ------>| Divisor / Tick Generator |---- sec_tick --->+
 speed_sel ---->| (1x,1.5x,2x)            |                  |
                +--------------------------+                  v
                                                           +-------------------+
start ---------->                                          | Control + Counter |
target_min ------> +--------------------------+            |   MM:SS BCD       |---- done_led
target_sec_t ----->| Validación de tiempo     |----------->| stop al objetivo  |
target_sec_u ----->| 0:00 .. 5:00             |            +-------------------+
                   +--------------------------+                     |
                                                                    v
                                                    cur_min, cur_sec_t, cur_sec_u

speed_sel -------------------------------------> Decodificador de velocidad
                                                  -> speed_1x, speed_1_5x, speed_2x
```

---

## 3) Código VHDL completo y funcional

Archivo: `voice_note_player.vhd`

> Incluye entidad + arquitectura RTL en un solo archivo para facilitar simulación/síntesis en cursos.

---

## 4) ¿Cómo se implementa cada velocidad?

- **1x**
  - `sec_tick` cada 1 segundo real.
  - El contador avanza +1 segundo por tick.

- **2x**
  - `sec_tick` cada 0.5 segundos reales (`CLK_HZ/2`).
  - El contador avanza +1 segundo por tick.
  - Resultado: el tiempo lógico avanza el doble.

- **1.5x**
  - Base temporal de 1 segundo real.
  - Se alterna el incremento del contador: un ciclo suma +1 segundo y el siguiente suma +2 segundos.
  - Promedio: `(1 + 2) / 2 = 1.5` segundos lógicos por segundo real.

---

## 5) Sugerencias para implementarlo en Logisim

1. **Bloque de reloj**: usa `Clock` + `Counter` para dividir frecuencia hasta 1 Hz y 2 Hz.
2. **Selector de velocidad**:
   - Multiplexor para elegir qué tick usar (1 Hz, 2 Hz, y patrón 1.5x).
3. **1.5x en Logisim**:
   - Implementa un flip-flop que alterne estado (`0/1`) cada segundo.
   - Si estado=0 suma 1; si estado=1 suma 2.
4. **Contador MM:SS**:
   - Tres contadores BCD encadenados: segundos unidades (0..9), segundos decenas (0..5), minutos (0..5).
5. **Comparador de fin**:
   - Comparadores de igualdad para MM:SS actual vs objetivo.
   - Cuando coincide: latch/flag de fin + detener enable de contador.
6. **Displays**:
   - Cada dígito BCD a decodificador de 7 segmentos.
   - Velocidad con 3 LEDs o texto en display auxiliar.

