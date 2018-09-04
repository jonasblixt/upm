EESchema Schematic File Version 4
EELAYER 26 0
EELAYER END
$Descr A3 16535 11693
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L cpu:ATSAMD21E15B U1
U 1 1 5B8EF43F
P 2750 5250
F 0 "U1" H 3125 8047 60  0000 C CNN
F 1 "ATSAMD21E15B" H 3125 7941 60  0000 C CNN
F 2 "footprints:QFN-32-1EP_5x5mm_Pitch0.5mm" H 3250 8100 60  0001 C CNN
F 3 "" H 2750 5250 60  0001 C CNN
F 4 "Microchip" H 3250 8400 60  0001 C CNN "Manufacturer"
F 5 "ATSAMD21E15B-MUT" H 3300 8250 60  0001 C CNN "Part Number"
	1    2750 5250
	1    0    0    -1  
$EndComp
$Comp
L comm:USB2512B U3
U 1 1 5B8EF4E0
P 5900 4750
F 0 "U3" H 6775 7987 60  0000 C CNN
F 1 "USB2512B" H 6775 7881 60  0000 C CNN
F 2 "footprints:QFN-36-1EP_6x6mm_Pitch0.5mm" H 6400 8200 60  0001 C CNN
F 3 "" H 5950 7850 60  0001 C CNN
F 4 "Microchip" H 6400 8400 60  0001 C CNN "Manufacturer"
F 5 "USB2512Bi-AEZG" H 6400 8300 60  0001 C CNN "Part Number"
	1    5900 4750
	1    0    0    -1  
$EndComp
$Comp
L power:PAC1934 U4
U 1 1 5B8EF55F
P 9150 4950
F 0 "U4" H 9725 6247 60  0000 C CNN
F 1 "PAC1934" H 9725 6141 60  0000 C CNN
F 2 "footprints:QFN-16-1EP_4x4mm_Pitch0.65mm" H 9550 6200 60  0001 C CNN
F 3 "" H 9150 4950 60  0001 C CNN
F 4 "Microchip" H 9600 6400 60  0001 C CNN "Manufacturer"
F 5 "PAC1934T-I/JQ" H 9750 6300 60  0001 C CNN "Part Number"
	1    9150 4950
	1    0    0    -1  
$EndComp
$Comp
L power:LP3470M5-3.08 U5
U 1 1 5B8EF60F
P 9650 2050
F 0 "U5" H 9975 2547 60  0000 C CNN
F 1 "LP3470M5-3.08" H 9975 2441 60  0000 C CNN
F 2 "" H 9250 1850 60  0000 C CNN
F 3 "" H 9250 1850 60  0000 C CNN
	1    9650 2050
	1    0    0    -1  
$EndComp
$Comp
L power:NCP380HSNAJAAT1G U6
U 1 1 5B8EF6E4
P 9750 2700
F 0 "U6" H 10100 3197 60  0000 C CNN
F 1 "NCP380HSNAJAAT1G" H 10100 3091 60  0000 C CNN
F 2 "" H 9750 2700 60  0000 C CNN
F 3 "" H 9750 2700 60  0000 C CNN
	1    9750 2700
	1    0    0    -1  
$EndComp
$Comp
L dcdc:MIC23150-SYMT U2
U 1 1 5B8EF888
P 4050 6700
F 0 "U2" H 4400 7491 79  0000 C CNN
F 1 "MIC23150-SYMT" H 4400 7356 79  0000 C CNN
F 2 "DFN-8_2x2mm_Pitch0.5mm" H 4500 7850 79  0001 C CNN
F 3 "" H 4150 7350 79  0001 C CNN
F 4 "MIC23150-SYMT" H 4250 7450 79  0001 C CNN "Part Number"
F 5 "Microchip" H 4350 7550 79  0001 C CNN "Manufacturer"
	1    4050 6700
	1    0    0    -1  
$EndComp
$Comp
L connectors:USB_A_292303-1 J2
U 1 1 5B8EFDA0
P 12850 1800
F 0 "J2" H 13078 2086 60  0000 L CNN
F 1 "USB_A_292303-1" H 13078 1980 60  0000 L CNN
F 2 "" H 12850 1800 60  0001 C CNN
F 3 "" H 12850 1800 60  0001 C CNN
F 4 "TE" H 13000 2500 60  0001 C CNN "Manufacturer"
F 5 "292303-1" H 13100 2600 60  0001 C CNN "Part Number"
	1    12850 1800
	1    0    0    -1  
$EndComp
$Comp
L connectors:FTSH-105-01-F-DV-K J1
U 1 1 5B8EFE4C
P 12550 2700
F 0 "J1" H 12550 3125 50  0000 C CNN
F 1 "FTSH-105-01-F-DV-K" H 12550 3034 50  0000 C CNN
F 2 "Jonas:FTSH-105-01-F-DV-K" H 12650 3300 50  0001 C CNN
F 3 "" H 12550 2700 50  0001 C CNN
F 4 "Samtec" H 12600 3100 50  0001 C CNN "Manufacturer"
F 5 "FTSH-105-01-F-DV-K.stp" H 12700 3200 50  0001 C CNN "Part Number"
	1    12550 2700
	1    0    0    -1  
$EndComp
$EndSCHEMATC