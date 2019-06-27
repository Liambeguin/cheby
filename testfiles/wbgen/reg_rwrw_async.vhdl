library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity reg1 is
  port (
    rst_n_i              : in    std_logic;
    clk_sys_i            : in    std_logic;
    wb_dat_i             : in    std_logic_vector(31 downto 0);
    wb_dat_o             : out   std_logic_vector(31 downto 0);
    wb_cyc_i             : in    std_logic;
    wb_sel_i             : in    std_logic_vector(3 downto 0);
    wb_stb_i             : in    std_logic;
    wb_we_i              : in    std_logic;
    wb_ack_o             : out   std_logic;
    wb_stall_o           : out   std_logic;
    clk1                 : in    std_logic;
    -- Ports for asynchronous (clock: clk1) std_logic_vector field: 'Reset bit' in reg: 'Register 1'
    reg1_r1_reset_o      : out   std_logic_vector(1 downto 0);
    reg1_r1_reset_i      : in    std_logic_vector(1 downto 0);
    reg1_r1_reset_load_o : out   std_logic
  );
end reg1;

architecture syn of reg1 is

  signal reg1_r1_reset_int_read         : std_logic_vector(1 downto 0);
  signal reg1_r1_reset_int_write        : std_logic_vector(1 downto 0);
  signal reg1_r1_reset_lw               : std_logic;
  signal reg1_r1_reset_lw_delay         : std_logic;
  signal reg1_r1_reset_lw_read_in_progress : std_logic;
  signal reg1_r1_reset_lw_s0            : std_logic;
  signal reg1_r1_reset_lw_s1            : std_logic;
  signal reg1_r1_reset_lw_s2            : std_logic;
  signal reg1_r1_reset_rwsel            : std_logic;
  signal ack_sreg                       : std_logic_vector(9 downto 0);
  signal rddata_reg                     : std_logic_vector(31 downto 0);
  signal wrdata_reg                     : std_logic_vector(31 downto 0);
  signal bwsel_reg                      : std_logic_vector(3 downto 0);
  signal rwaddr_reg                     : std_logic_vector(0 downto 0);
  signal ack_in_progress                : std_logic;
  signal wr_int                         : std_logic;
  signal rd_int                         : std_logic;
  signal allones                        : std_logic_vector(31 downto 0);
  signal allzeros                       : std_logic_vector(31 downto 0);

begin
  -- Some internal signals assignments. For (foreseen) compatibility with other bus standards.
  wrdata_reg <= wb_dat_i;
  bwsel_reg <= wb_sel_i;
  rd_int <= wb_cyc_i and (wb_stb_i and (not wb_we_i));
  wr_int <= wb_cyc_i and (wb_stb_i and wb_we_i);
  allones <= (others => '1');
  allzeros <= (others => '0');
  -- 
  -- Main register bank access process.
  process (clk_sys_i, rst_n_i)
  begin
    if (rst_n_i = '0') then
      ack_sreg <= "0000000000";
      ack_in_progress <= '0';
      rddata_reg <= "00000000000000000000000000000000";
      reg1_r1_reset_lw <= '0';
      reg1_r1_reset_lw_delay <= '0';
      reg1_r1_reset_lw_read_in_progress <= '0';
      reg1_r1_reset_rwsel <= '0';
      reg1_r1_reset_int_write <= "00";
    elsif rising_edge(clk_sys_i) then
      -- advance the ACK generator shift register
      ack_sreg(8 downto 0) <= ack_sreg(9 downto 1);
      ack_sreg(9) <= '0';
      if (ack_in_progress = '1') then
        if (ack_sreg(0) = '1') then
          ack_in_progress <= '0';
        else
          reg1_r1_reset_lw <= reg1_r1_reset_lw_delay;
          reg1_r1_reset_lw_delay <= '0';
          if ((ack_sreg(1) = '1') and (reg1_r1_reset_lw_read_in_progress = '1')) then
            rddata_reg(1 downto 0) <= reg1_r1_reset_int_read;
            reg1_r1_reset_lw_read_in_progress <= '0';
          end if;
        end if;
      else
        if ((wb_cyc_i = '1') and (wb_stb_i = '1')) then
          if (wb_we_i = '1') then
            reg1_r1_reset_int_write <= wrdata_reg(1 downto 0);
            reg1_r1_reset_lw <= '1';
            reg1_r1_reset_lw_delay <= '1';
            reg1_r1_reset_lw_read_in_progress <= '0';
            reg1_r1_reset_rwsel <= '1';
          end if;
          if (wb_we_i = '0') then
            reg1_r1_reset_lw <= '1';
            reg1_r1_reset_lw_delay <= '1';
            reg1_r1_reset_lw_read_in_progress <= '1';
            reg1_r1_reset_rwsel <= '0';
          end if;
          rddata_reg(2) <= 'X';
          rddata_reg(3) <= 'X';
          rddata_reg(4) <= 'X';
          rddata_reg(5) <= 'X';
          rddata_reg(6) <= 'X';
          rddata_reg(7) <= 'X';
          rddata_reg(8) <= 'X';
          rddata_reg(9) <= 'X';
          rddata_reg(10) <= 'X';
          rddata_reg(11) <= 'X';
          rddata_reg(12) <= 'X';
          rddata_reg(13) <= 'X';
          rddata_reg(14) <= 'X';
          rddata_reg(15) <= 'X';
          rddata_reg(16) <= 'X';
          rddata_reg(17) <= 'X';
          rddata_reg(18) <= 'X';
          rddata_reg(19) <= 'X';
          rddata_reg(20) <= 'X';
          rddata_reg(21) <= 'X';
          rddata_reg(22) <= 'X';
          rddata_reg(23) <= 'X';
          rddata_reg(24) <= 'X';
          rddata_reg(25) <= 'X';
          rddata_reg(26) <= 'X';
          rddata_reg(27) <= 'X';
          rddata_reg(28) <= 'X';
          rddata_reg(29) <= 'X';
          rddata_reg(30) <= 'X';
          rddata_reg(31) <= 'X';
          ack_sreg(5) <= '1';
          ack_in_progress <= '1';
        end if;
      end if;
    end if;
  end process;


  -- Drive the data output bus
  wb_dat_o <= rddata_reg;
  -- Reset bit
  -- asynchronous std_logic_vector register : Reset bit (type RW/WO, clk1 <-> clk_sys_i)
  process (clk1, rst_n_i)
  begin
    if (rst_n_i = '0') then
      reg1_r1_reset_lw_s0 <= '0';
      reg1_r1_reset_lw_s1 <= '0';
      reg1_r1_reset_lw_s2 <= '0';
      reg1_r1_reset_o <= "00";
      reg1_r1_reset_load_o <= '0';
      reg1_r1_reset_int_read <= "00";
    elsif rising_edge(clk1) then
      reg1_r1_reset_lw_s0 <= reg1_r1_reset_lw;
      reg1_r1_reset_lw_s1 <= reg1_r1_reset_lw_s0;
      reg1_r1_reset_lw_s2 <= reg1_r1_reset_lw_s1;
      if ((reg1_r1_reset_lw_s2 = '0') and (reg1_r1_reset_lw_s1 = '1')) then
        if (reg1_r1_reset_rwsel = '1') then
          reg1_r1_reset_o <= reg1_r1_reset_int_write;
          reg1_r1_reset_load_o <= '1';
        else
          reg1_r1_reset_load_o <= '0';
          reg1_r1_reset_int_read <= reg1_r1_reset_i;
        end if;
      else
        reg1_r1_reset_load_o <= '0';
      end if;
    end if;
  end process;


  rwaddr_reg <= (others => '0');
  wb_stall_o <= (not ack_sreg(0)) and (wb_stb_i and wb_cyc_i);
  -- ACK signal generation. Just pass the LSB of ACK counter.
  wb_ack_o <= ack_sreg(0);
end syn;
