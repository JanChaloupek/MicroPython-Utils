while True:
    vek_input = input("Zadej věk cestujícího: ")
    if vek_input.isdigit():
        vek = int(vek_input)
        break
    else:
        print("Zadej prosím číslo!")
while True:
    zamestnanec = input("Je cestující zaměstnanec? (ano/ne): ").lower()
    if zamestnanec == "ano" or zamestnanec == "ne":
        break
    else:
        print("Zadej pouze 'ano' nebo 'ne'!")

cena = 45

if zamestnanec == "ano":
    if vek > 55:
        cena = 0
    else:
        cena = cena * 0.2
else:
    if vek < 12:
        cena = 0
    elif vek < 18:
        cena = cena * 0.5
    elif vek > 65:
        cena = cena * 0.7

print("Konečná cena jízdenky je:", cena, "Kč")
