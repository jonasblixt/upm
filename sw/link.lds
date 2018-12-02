OUTPUT_FORMAT("elf32-littlearm")
OUTPUT_ARCH("arm")

MEMORY
{
    flash (rw)  : ORIGIN = 0x00000000, LENGTH = 32K
    sram (rwx)  : ORIGIN = 0x20000000, LENGTH = 4K
}

ENTRY(reset_handler)

SECTIONS
{
    . = ORIGIN(flash);

    .vectors :
    {
        KEEP(*(.vectors .vectors.*))
    } > flash

    .text :
    {
        _stext = .;
        *(.rodata .rodata*);
        *(.text .text*);
        . = ALIGN(4);
        _etext = .;
    } > flash

    . = ALIGN(4);

    .relocate : AT(_etext)
    {
        _srelocate = .;
        *(.data .data.*);
        . = ALIGN(4);
        _erelocate = .;
    } > sram
    
    . = ALIGN(4);

    .bss (NOLOAD) :
    {
        _sbss = .;
        *(.bss .bss.*)
        . = ALIGN(4);
        _ebss = .;
    } > sram

	.stack (NOLOAD):
	{
        . = ALIGN(8);
        _sstack = .;
		KEEP(*(.stack* .stack.*))
        _estack = .;
	} > sram

}
