# DCAU Watch Guide - Version 4.1 (Continuous Loop and Turkish Character Fix)

print("--- DCAU Rehberine Hoş Geldin! ---")
print("(Programdan çıkmak için 'exit' veya 'Çıkış' yazabilirsin.)\n")

# The timeline dictionary (Key: watched series, Value: next series to watch)
dcau_timeline = {
    "batman: the animated series": "The New Batman Adventures",
    "the new batman adventures": "Superman: the animated series",
    "superman: the animated series": "Batman Beyond",
    "batman beyond": "Justice League",
    "justice league": "Justice League Unlimited",
}

while True:
    # Get raw input from the user
    raw_input = input("DCAU evreninde en son hangi seriyi bitirdin? (Lütfen tam adını yaz): ")

    if raw_input.lower().strip() in ["exit", "çıkış"]:
        print("Görüşmek üzere! İyi seyirler!")
        break

    # TURKISH CHARACTER FIX: Replace 'İ' and 'ı' with 'i' BEFORE lowercasing
    cleaned_input = raw_input.replace("İ", "i").replace("ı", "i")

    # Clean the input (lowercase, split by spaces, join with a single space)
    last_watched = " ".join(cleaned_input.lower().split())

    # Check if the user's input exists as a 'key' in our dictionary
    if last_watched in dcau_timeline:
        next_show = dcau_timeline[last_watched]
        print("Harika ilerliyorsun! Sıradaki hedefin: ", next_show)
    else:
        print("Hmmm, Listemde bu isme göre bir yönlendirme yok. Acaba ismini mi yanlış yazdın?")