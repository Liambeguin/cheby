library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity m1 is
  port (
    Clk                  : in    std_logic;
    Rst                  : in    std_logic;
    VMEAddr              : in    std_logic_vector(2 downto 2);
    VMERdData            : out   std_logic_vector(31 downto 0);
    VMEWrData            : in    std_logic_vector(31 downto 0);
    VMERdMem             : in    std_logic;
    VMEWrMem             : in    std_logic;
    VMERdDone            : out   std_logic;
    VMEWrDone            : out   std_logic;

    -- REG r1
    r1_o                 : out   std_logic_vector(63 downto 0)
  );
end m1;

architecture syn of m1 is
  signal rst_n                          : std_logic;
  signal rd_ack_int                     : std_logic;
  signal wr_ack_int                     : std_logic;
  signal r1_reg                         : std_logic_vector(63 downto 0);
  signal r1_wreq                        : std_logic_vector(1 downto 0);
  signal r1_wack                        : std_logic_vector(1 downto 0);
  signal rd_ack_d0                      : std_logic;
  signal rd_dat_d0                      : std_logic_vector(31 downto 0);
  signal wr_req_d0                      : std_logic;
  signal wr_adr_d0                      : std_logic_vector(2 downto 2);
  signal wr_dat_d0                      : std_logic_vector(31 downto 0);
begin
  rst_n <= not Rst;
  VMERdDone <= rd_ack_int;
  VMEWrDone <= wr_ack_int;

  -- pipelining for wr-in+rd-out
  process (Clk) begin
    if rising_edge(Clk) then
      if rst_n = '0' then
        rd_ack_int <= '0';
        wr_req_d0 <= '0';
      else
        rd_ack_int <= rd_ack_d0;
        VMERdData <= rd_dat_d0;
        wr_req_d0 <= VMEWrMem;
        wr_adr_d0 <= VMEAddr;
        wr_dat_d0 <= VMEWrData;
      end if;
    end if;
  end process;

  -- Register r1
  r1_o <= r1_reg;
  process (Clk) begin
    if rising_edge(Clk) then
      if rst_n = '0' then
        r1_reg <= "0000000000000000000000000000000000000000000000000000000000000000";
        r1_wack <= (others => '0');
      else
        if r1_wreq(0) = '1' then
          r1_reg(31 downto 0) <= wr_dat_d0;
        else
          r1_reg(31 downto 0) <= "00000000000000000000000000000000";
        end if;
        if r1_wreq(1) = '1' then
          r1_reg(63 downto 32) <= wr_dat_d0;
        else
          r1_reg(63 downto 32) <= "00000000000000000000000000000000";
        end if;
        r1_wack <= r1_wreq;
      end if;
    end if;
  end process;

  -- Process for write requests.
  process (wr_adr_d0, wr_req_d0, r1_wack) begin
    r1_wreq <= (others => '0');
    case wr_adr_d0(2 downto 2) is
    when "0" =>
      -- Reg r1
      r1_wreq(1) <= wr_req_d0;
      wr_ack_int <= r1_wack(1);
    when "1" =>
      -- Reg r1
      r1_wreq(0) <= wr_req_d0;
      wr_ack_int <= r1_wack(0);
    when others =>
      wr_ack_int <= wr_req_d0;
    end case;
  end process;

  -- Process for read requests.
  process (VMEAddr, VMERdMem) begin
    -- By default ack read requests
    rd_dat_d0 <= (others => 'X');
    case VMEAddr(2 downto 2) is
    when "0" =>
      -- Reg r1
      rd_ack_d0 <= VMERdMem;
      rd_dat_d0 <= "00000000000000000000000000000000";
    when "1" =>
      -- Reg r1
      rd_ack_d0 <= VMERdMem;
      rd_dat_d0 <= "00000000000000000000000000000000";
    when others =>
      rd_ack_d0 <= VMERdMem;
    end case;
  end process;
end syn;
