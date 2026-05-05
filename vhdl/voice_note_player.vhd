library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- ============================================================
-- Top: Voice note playback timer (up to 5:00) with speed select
-- Speeds:
--   speed_sel = "00" -> 1x
--   speed_sel = "01" -> 1.5x
--   speed_sel = "10" -> 2x
-- ============================================================
entity voice_note_player is
  generic (
    CLK_HZ : integer := 50000000  -- Board clock frequency
  );
  port (
    clk           : in  std_logic;
    rst           : in  std_logic;
    start         : in  std_logic;
    speed_sel     : in  std_logic_vector(1 downto 0);
    target_min    : in  std_logic_vector(2 downto 0); -- 0..5
    target_sec_t  : in  std_logic_vector(2 downto 0); -- tens: 0..5
    target_sec_u  : in  std_logic_vector(3 downto 0); -- units: 0..9

    cur_min       : out std_logic_vector(2 downto 0);
    cur_sec_t     : out std_logic_vector(2 downto 0);
    cur_sec_u     : out std_logic_vector(3 downto 0);

    speed_1x      : out std_logic;
    speed_1_5x    : out std_logic;
    speed_2x      : out std_logic;

    done_led      : out std_logic
  );
end entity;

architecture rtl of voice_note_player is
  signal run          : std_logic := '0';
  signal sec_tick     : std_logic := '0';
  signal min_cnt      : unsigned(2 downto 0) := (others => '0');
  signal sec_t_cnt    : unsigned(2 downto 0) := (others => '0');
  signal sec_u_cnt    : unsigned(3 downto 0) := (others => '0');

  signal tgt_min_u    : unsigned(2 downto 0);
  signal tgt_sec_t_u  : unsigned(2 downto 0);
  signal tgt_sec_u_u  : unsigned(3 downto 0);

  signal done_int     : std_logic := '0';
  signal cycle_count  : integer range 0 to 2 := 0; -- Used for 1.5x pattern

  function is_invalid_time(
    m : unsigned(2 downto 0);
    t : unsigned(2 downto 0);
    u : unsigned(3 downto 0)
  ) return boolean is
  begin
    if (m > 5) then
      return true;
    elsif (t > 5) then
      return true;
    elsif (u > 9) then
      return true;
    elsif (m = 5 and (t /= 0 or u /= 0)) then
      return true;
    else
      return false;
    end if;
  end function;

begin
  tgt_min_u   <= unsigned(target_min);
  tgt_sec_t_u <= unsigned(target_sec_t);
  tgt_sec_u_u <= unsigned(target_sec_u);

  -- One-hot speed indication
  speed_1x   <= '1' when speed_sel = "00" else '0';
  speed_1_5x <= '1' when speed_sel = "01" else '0';
  speed_2x   <= '1' when speed_sel = "10" else '0';

  -- ============================================================
  -- Tick generator with selectable speed
  -- ============================================================
  tick_gen : process(clk, rst)
    variable div_count : integer := 0;
    variable div_limit : integer := CLK_HZ - 1;
  begin
    if rst = '1' then
      div_count   := 0;
      sec_tick    <= '0';
      cycle_count <= 0;
    elsif rising_edge(clk) then
      sec_tick <= '0';

      if speed_sel = "10" then
        -- 2x: tick every 0.5 s
        div_limit := (CLK_HZ/2) - 1;
      else
        -- 1x and base for 1.5x
        div_limit := CLK_HZ - 1;
      end if;

      if div_count = div_limit then
        div_count := 0;

        if speed_sel = "01" then
          -- 1.5x using pattern over 2 seconds:
          -- second 0: +1 second
          -- second 1: +2 seconds
          -- average = 3 seconds / 2 real seconds
          if cycle_count = 0 then
            sec_tick    <= '1';
            cycle_count <= 1;
          else
            sec_tick    <= '1';
            cycle_count <= 0;
          end if;
        else
          sec_tick <= '1';
        end if;
      else
        div_count := div_count + 1;
      end if;
    end if;
  end process;

  -- ============================================================
  -- Main control + counter
  -- ============================================================
  control_count : process(clk, rst)
    variable extra_inc : boolean;
  begin
    if rst = '1' then
      run       <= '0';
      done_int  <= '0';
      min_cnt   <= (others => '0');
      sec_t_cnt <= (others => '0');
      sec_u_cnt <= (others => '0');
    elsif rising_edge(clk) then
      if start = '1' and run = '0' then
        if not is_invalid_time(tgt_min_u, tgt_sec_t_u, tgt_sec_u_u) then
          run       <= '1';
          done_int  <= '0';
          min_cnt   <= (others => '0');
          sec_t_cnt <= (others => '0');
          sec_u_cnt <= (others => '0');
        end if;
      end if;

      if run = '1' and sec_tick = '1' then
        -- Increment one second
        if sec_u_cnt = 9 then
          sec_u_cnt <= (others => '0');
          if sec_t_cnt = 5 then
            sec_t_cnt <= (others => '0');
            if min_cnt < 5 then
              min_cnt <= min_cnt + 1;
            end if;
          else
            sec_t_cnt <= sec_t_cnt + 1;
          end if;
        else
          sec_u_cnt <= sec_u_cnt + 1;
        end if;

        -- For 1.5x, every second cycle we add one extra second
        extra_inc := false;
        if speed_sel = "01" and cycle_count = 0 then
          extra_inc := true;
        end if;

        if extra_inc then
          if sec_u_cnt = 8 then
            sec_u_cnt <= to_unsigned(0, 4);
            if sec_t_cnt = 5 then
              sec_t_cnt <= to_unsigned(0, 3);
              if min_cnt < 5 then
                min_cnt <= min_cnt + 1;
              end if;
            else
              sec_t_cnt <= sec_t_cnt + 1;
            end if;
          elsif sec_u_cnt = 9 then
            sec_u_cnt <= to_unsigned(1, 4);
            if sec_t_cnt = 5 then
              sec_t_cnt <= to_unsigned(0, 3);
              if min_cnt < 5 then
                min_cnt <= min_cnt + 1;
              end if;
            else
              sec_t_cnt <= sec_t_cnt + 1;
            end if;
          else
            sec_u_cnt <= sec_u_cnt + 2;
          end if;
        end if;

        -- Stop when reaches configured target
        if (min_cnt = tgt_min_u and sec_t_cnt = tgt_sec_t_u and sec_u_cnt = tgt_sec_u_u) then
          run      <= '0';
          done_int <= '1';
        end if;
      end if;
    end if;
  end process;

  done_led  <= done_int;
  cur_min   <= std_logic_vector(min_cnt);
  cur_sec_t <= std_logic_vector(sec_t_cnt);
  cur_sec_u <= std_logic_vector(sec_u_cnt);

end architecture;
