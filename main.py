def namen(namen_lijst):
    lijst = []
    for item in namen_lijst:
        lijst.append(item.capitalize())

    resultaat = ', '.join(lijst[:-1]) + ' en ' + lijst[-1]
    print(resultaat)


lijst_namen = ["mark", "elwyn", "nova", "frans"]
namen(lijst_namen)


