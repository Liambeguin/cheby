library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package MemMap_area_extarea_error is

  -- Ident Code
  constant C_area_extarea_error_IdentCode : std_logic_vector(15 downto 0) := X"00FF";

  -- Memory Map Version
  constant C_area_extarea_error_MemMapVersion : std_logic_vector(31 downto 0) := X"0133A207";--20161031
  constant C_Area_area_extarea_error_area : std_logic_vector(19 downto 19) := "1";
  -- Register Addresses : Area area
  constant C_Reg_area_extarea_error_area_test1_1 : std_logic_vector(18 downto 1) := "000000000000000000";-- : Word address : 0x00000; Byte Address : 0x00000
  constant C_Reg_area_extarea_error_area_test1_0 : std_logic_vector(18 downto 1) := "000000000000000001";-- : Word address : 0x00001; Byte Address : 0x00002

  -- Register Auto Clear Masks : Area area
  constant C_ACM_area_extarea_error_area_test1_1 : std_logic_vector(15 downto 8) := "00000000";-- : Value : X"00"
  constant C_ACM_area_extarea_error_area_test1_0 : std_logic_vector(7 downto 0) := "00000000";-- : Value : X"00"

  -- Register Preset Masks : Area area
  constant C_PSM_area_extarea_error_area_test1_1 : std_logic_vector(15 downto 8) := "00000000";-- : Value : X"00"
  constant C_PSM_area_extarea_error_area_test1_0 : std_logic_vector(7 downto 0) := "00000000";-- : Value : X"00"

  -- CODE FIELDS
  -- Memory Data : Area area
  -- Submap Addresses : Area area
  -- Register Addresses : Memory Map
  constant C_Reg_area_extarea_error_test1_1 : std_logic_vector(19 downto 1) := "0000000000000000000";-- : Word address : 0x00000; Byte Address : 0x00000
  constant C_Reg_area_extarea_error_test1_0 : std_logic_vector(19 downto 1) := "0000000000000000001";-- : Word address : 0x00001; Byte Address : 0x00002

  -- Register Auto Clear Masks : Memory Map
  constant C_ACM_area_extarea_error_test1_1 : std_logic_vector(15 downto 8) := "00000000";-- : Value : X"00"
  constant C_ACM_area_extarea_error_test1_0 : std_logic_vector(7 downto 0) := "00000000";-- : Value : X"00"

  -- Register Preset Masks : Memory Map
  constant C_PSM_area_extarea_error_test1_1 : std_logic_vector(15 downto 8) := "00000000";-- : Value : X"00"
  constant C_PSM_area_extarea_error_test1_0 : std_logic_vector(7 downto 0) := "00000000";-- : Value : X"00"

  -- CODE FIELDS
  -- Memory Data : Memory Map
  -- Submap Addresses : Memory Map
end MemMap_area_extarea_error;
