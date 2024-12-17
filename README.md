# CH341 Wrapper
*A Python module for interacting with flash chips using the CH341 programmer.*

---

## Description
The **CH341 Wrapper** provides a powerful and flexible Python interface for interacting with flash chips via the **CH341 programmer**. It allows users to perform targeted **read**, **write** and **erase** operations on specific pages without handling the entire chip contents, making it efficient for selective data manipulation.

> [!NOTE]
> This module is primarily developed and tested for **DS35M1GA** NAND Flash chips. It may or may not work with other devices that communicate via the **SPI interface**.


## Features
- Targeted read/write/erase operations on specific pages.
- Designed for NAND Flash chips (DS35M1GA).
- Includes the header file for further scalability.

## Requirements
- Python 3.x installed
- CH341DLL library (included in this repository)
- Compatible *CH341 programmer\**

