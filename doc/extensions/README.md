# Changelog
## core
### 1.0.0 -> 2.0.0
* merge 'note' with 'description'
## x-fesa:
### 1.0.0 -> 2.0.0
* split persistence=PPM/Fesa/None to persistence=true/false and multiplexed=true/false
## x-gena:
### 1.0.0 -> 2.0.0
* replace code-fields with x-enums extension


# Extensions Docmentation

In december 2019, we decided to add versioning for the schema of the
core specifications and for the schema of the extensions.

The schema version is defined using semantic versioning.

The current extensions are described in the following sections.
## <a name="x-map-info">x-map-info
This extension is the successor of [x-cern-info](#x-cern-info) and some attributes previously used in x-gena as well.

It contains 2 possible attributes
*  ident
*  memmap-version

### ident
Ident is a unique identifier of a memory map which can be feed back to a ro register to provide information and identification about what type of board/firwmare the memory map belongs to.
The value itself is not standardized among the different CERN groups.

In RF we have a long standing list of idents (formarlly names ident-code in the old cheburashka based memory maps) for VME which are mastered centrally by John Molendijk (`john.molendijk@cern.ch`).
For uTCA based boards we start from scratch with a new list of idents. Currently there is no central person or location to award them and in fact the firmware does not yet provide any meaningful data. But a first [wiki page](https://wikis.cern.ch/pages/viewpage.action?pageId=122066518) has been created

* **Previous used ident-code attribute in x-cern-info/ident-code and x-gena/ident-code are migrated to x-map-info/ident**

### memmamp-version
The memorymap version attribut is now a semantic version only consisting of 3 parts with 8bits each. As an attribute value they have to be specified as a string separated by dots. The different parts are using the standard schema MAJOR.MINOR.PATCH as specified by [Semantic Versioning](https://semver.org)
These values are being exposed by according registers in the firmware/IP cores.

* **Previous x-cern-info/semantic-mem-map-version is migrated to x-map-info/memmap-version**
* **Previous x-gena/semantic-mem-map-version is migrated to x-map-info/memmap-version**
* **Previous x-gena/map-version which was a date-code is debriacted and should not longer be used in new maps**


## x-hdl

## x-gena
Attributes of this extension should NOT be used anymore with new designs. When using the new gen-cheby generation tool, this attributes are ignored! 


## x-fesa

Attributes provided by this extension should be mainly used and/or decided on together with the FESA class developer or HW designer with sufficient experience with FESA. 

* generate - default=True
* persistence - default=True
* multiplexed - default=True
* ... way more ..

### generate
This attribute allows to specify a boolean value \[True|False\]. By default (even if not present) the values is set to "True"

The FESA generator will create a matching field in the data store of the FESA class for each register if the attribute is not specified or explicitly declared with "True". If you want to avoid this because the data does not need to be stored anywhere (for example because you are reading it every time on the fly from the hardware) this attribute can be used to suppress generation of a field.

A warning should be issued if the value is set to "False" but additional attributes such as for example "persistence" or "multiplexed" are specified.

### persistence
This flag existed already in the past but it's usage was rather obscure. The previous functionality has been split into 2 attributes. One of them is the persistence attribute. It now does only what the name implies: If specified with "True" the according setting field in the data store will be marked as persistent as well; which means it's value is regularly written into the persistency file. Later one is used to restore the value(s) of the fields when a FESA processes is restarted. 
Thus it makes for example little sense to declare a status, fault or other acquisition field (aka ro register) as "persistence" as the state most likely has changed in the meantime.

### multiplexed
In the past FESA provided a attribute called multiplexed. As of FESA3 v.7.0.0 this has changed. Now they distinct between multiplexed (setting fields) and cycle-bound (acquisition fields). For the sake of simplicity in Reksio we provide only one attribute called "multiplexed". Depending of the type of the register the attribute belongs to, it is translated correctly to either of the 2 previous choices depending on the register type (ro, rw)



## x-driver-edge

TBD: For now this is just the list of existing attributes, further documentation needs to be added
* name
* equipment-code
* module-type
* vme-base-addr
* endianness
* bus-type
* board-type
* driver-version
* driver-version-suffix
* schema-version
* description
* default-pci-bar-name
* generate-separate-library
* dma-mode
* pci-device-info


### driver-version
Even there is no clean solution and clear solution yet on the CCDE side, it is possible to specify a specific version to be used for a specific hardware type. On the driver (generation) side versioniong is now supported. It therefore is mandatory to specify a version for your driver.
The GUI makes sure the version follows the constraints of MAJOR.MINO.PATCH format. This version is direclty feed into the CSV file generated by the Reksio GUI and used by edge to generate a driver.

### driver-version-suffix
With the limitation to MAJOR.MINO.PATCH for production the feature of re-releasing a driver is prevented by intention. In order to deal with this during development, this attribute allows  the use of an arbitrary suffix i.e. "_dev".



### pci-device-info

The PCI device info is mandatory for PCI modules as the kernel idenifies the board with this ID in order to know which driver to load to access the hardware.

TBD: Format

It is possible to not add all of the attributes if you have a driver which fits more than one card.

* vendor-id
* device-id
* subvendor-id
* subdevice-id

### x-drive-edge child
Beside the attributes above x-driver-edge provides to elements (children) to be specified

* pci-bars
* ip-core-descriptions

#### pci-bars
Obviously, declartion of this element is only necessary for PCI based platforms. Add as many bars as you have defined in your (Vivado) project.
Each bar needs to have a (unique) name and (unique) number according to the PCI standard. If not specified explicitely, the start address for anything placed inside this bar is 0x0. 

* name : String, unique name. Best practice is barX where X is the bar number
* number : Positive integer number in the range of valid bars according to the PCI standard
* description : Allows to put a description how this bar is used
* base-addr : Allow to specify an offset to every single element (submap, register, etc.) added to this bar


## x-conversions

## x-wbgen

## x-devicetree

## x-interrupts

## x-enums
Enumerations - reusable replacement of x-gena/code-fields. Each enumeration must have:
* name
* width
* (optional) description
* (optional) comment
* items (as children)

Enumerations are defined under a memory-map element as its children. 
They can be referenced (used) by reg and field nodes, using x-enums/name attribute.

Each enumeration item contains:
* name
* value
* (optional) description
* (optional) comment

# Deprecated extensions

## <a name="x-cern-info">x-cern-info
This attribute is deprecated! Please use [x-map-info](#x-map-info)
