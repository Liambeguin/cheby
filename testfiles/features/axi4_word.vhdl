library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity sreg is
  port (
    aclk                 : in    std_logic;
    areset_n             : in    std_logic;
    awvalid              : in    std_logic;
    awready              : out   std_logic;
    awaddr               : in    std_logic_vector(2 downto 2);
    awprot               : in    std_logic_vector(2 downto 0);
    wvalid               : in    std_logic;
    wready               : out   std_logic;
    wdata                : in    std_logic_vector(31 downto 0);
    wstrb                : in    std_logic_vector(3 downto 0);
    bvalid               : out   std_logic;
    bready               : in    std_logic;
    bresp                : out   std_logic_vector(1 downto 0);
    arvalid              : in    std_logic;
    arready              : out   std_logic;
    araddr               : in    std_logic_vector(2 downto 2);
    arprot               : in    std_logic_vector(2 downto 0);
    rvalid               : out   std_logic;
    rready               : in    std_logic;
    rdata                : out   std_logic_vector(31 downto 0);
    rresp                : out   std_logic_vector(1 downto 0);

    -- REG areg
    areg_o               : out   std_logic_vector(31 downto 0);

    -- REG breg
    breg_o               : out   std_logic_vector(31 downto 0)
  );
end sreg;

architecture syn of sreg is
  signal wr_req                         : std_logic;
  signal wr_ack                         : std_logic;
  signal wr_addr                        : std_logic_vector(2 downto 2);
  signal wr_data                        : std_logic_vector(31 downto 0);
  signal wr_strb                        : std_logic_vector(3 downto 0);
  signal axi_awset                      : std_logic;
  signal axi_wset                       : std_logic;
  signal axi_wdone                      : std_logic;
  signal rd_req                         : std_logic;
  signal rd_ack                         : std_logic;
  signal rd_addr                        : std_logic_vector(2 downto 2);
  signal rd_data                        : std_logic_vector(31 downto 0);
  signal axi_arset                      : std_logic;
  signal axi_rdone                      : std_logic;
  signal areg_reg                       : std_logic_vector(31 downto 0);
  signal areg_wreq                      : std_logic;
  signal areg_wack                      : std_logic;
  signal breg_reg                       : std_logic_vector(31 downto 0);
  signal breg_wreq                      : std_logic;
  signal breg_wack                      : std_logic;
  signal rd_ack_d0                      : std_logic;
  signal rd_dat_d0                      : std_logic_vector(31 downto 0);
  signal wr_req_d0                      : std_logic;
  signal wr_adr_d0                      : std_logic_vector(2 downto 2);
  signal wr_dat_d0                      : std_logic_vector(31 downto 0);
  signal wr_sel_d0                      : std_logic_vector(3 downto 0);
begin

  -- AW, W and B channels
  awready <= not axi_awset;
  wready <= not axi_wset;
  bvalid <= axi_wdone;
  process (aclk) begin
    if rising_edge(aclk) then
      if areset_n = '0' then
        wr_req <= '0';
        axi_awset <= '0';
        axi_wset <= '0';
        axi_wdone <= '0';
      else
        wr_req <= '0';
        if awvalid = '1' and axi_awset = '0' then
          wr_addr <= awaddr;
          axi_awset <= '1';
          wr_req <= axi_wset;
        end if;
        if wvalid = '1' and axi_wset = '0' then
          wr_data <= wdata;
          wr_strb <= wstrb;
          axi_wset <= '1';
          wr_req <= axi_awset or awvalid;
        end if;
        if (axi_wdone and bready) = '1' then
          axi_wset <= '0';
          axi_awset <= '0';
          axi_wdone <= '0';
        end if;
        if wr_ack = '1' then
          axi_wdone <= '1';
        end if;
      end if;
    end if;
  end process;
  bresp <= "00";

  -- AR and R channels
  arready <= not axi_arset;
  rvalid <= axi_rdone;
  process (aclk) begin
    if rising_edge(aclk) then
      if areset_n = '0' then
        rd_req <= '0';
        axi_arset <= '0';
        axi_rdone <= '0';
        rdata <= (others => '0');
      else
        rd_req <= '0';
        if arvalid = '1' and axi_arset = '0' then
          rd_addr <= araddr;
          axi_arset <= '1';
          rd_req <= '1';
        end if;
        if (axi_rdone and rready) = '1' then
          axi_arset <= '0';
          axi_rdone <= '0';
        end if;
        if rd_ack = '1' then
          axi_rdone <= '1';
          rdata <= rd_data;
        end if;
      end if;
    end if;
  end process;
  rresp <= "00";

  -- pipelining for wr-in+rd-out
  process (aclk) begin
    if rising_edge(aclk) then
      if areset_n = '0' then
        rd_ack <= '0';
        wr_req_d0 <= '0';
      else
        rd_ack <= rd_ack_d0;
        rd_data <= rd_dat_d0;
        wr_req_d0 <= wr_req;
        wr_adr_d0 <= wr_addr;
        wr_dat_d0 <= wr_data;
        wr_sel_d0 <= wr_strb;
      end if;
    end if;
  end process;

  -- Register areg
  areg_o <= areg_reg;
  process (aclk) begin
    if rising_edge(aclk) then
      if areset_n = '0' then
        areg_reg <= "00000000000000000000000000000000";
        areg_wack <= '0';
      else
        if areg_wreq = '1' then
          areg_reg <= wr_dat_d0;
        end if;
        areg_wack <= areg_wreq;
      end if;
    end if;
  end process;

  -- Register breg
  breg_o <= breg_reg;
  process (aclk) begin
    if rising_edge(aclk) then
      if areset_n = '0' then
        breg_reg <= "00000000000000000000000000000000";
        breg_wack <= '0';
      else
        if breg_wreq = '1' then
          breg_reg <= wr_dat_d0;
        end if;
        breg_wack <= breg_wreq;
      end if;
    end if;
  end process;

  -- Process for write requests.
  process (wr_adr_d0, wr_req_d0, areg_wack, breg_wack) begin
    areg_wreq <= '0';
    breg_wreq <= '0';
    case wr_adr_d0(2 downto 2) is
    when "0" =>
      -- Reg areg
      areg_wreq <= wr_req_d0;
      wr_ack <= areg_wack;
    when "1" =>
      -- Reg breg
      breg_wreq <= wr_req_d0;
      wr_ack <= breg_wack;
    when others =>
      wr_ack <= wr_req_d0;
    end case;
  end process;

  -- Process for read requests.
  process (rd_addr, rd_req, areg_reg, breg_reg) begin
    -- By default ack read requests
    rd_dat_d0 <= (others => 'X');
    case rd_addr(2 downto 2) is
    when "0" =>
      -- Reg areg
      rd_ack_d0 <= rd_req;
      rd_dat_d0 <= areg_reg;
    when "1" =>
      -- Reg breg
      rd_ack_d0 <= rd_req;
      rd_dat_d0 <= breg_reg;
    when others =>
      rd_ack_d0 <= rd_req;
    end case;
  end process;
end syn;
