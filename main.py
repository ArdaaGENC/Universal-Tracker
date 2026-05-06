# DCAU İzleme Rehberi - Versiyon 2.0 (Etkileşimli)

print("--- DCAU Rehberine Hoş Geldin! ---")

# input() ile ekrana bir soru yazdırıp, cevabı 'son_izlenen' değişkenine kaydediyoruz.
son_izlenen = input("DCAU evreninde en son hangi seriyi bitirdin? (Lütfen tam adını yaz): ")

# Kullanıcının girdiği cevaba göre if/else mantığıyla karar veriyoruz.
if son_izlenen == "Batman: The Animated Series":
    print("Harika bir klasik! Sıradaki hedefin: The New Batman Adventures")

elif son_izlenen == "The New Batman Adventures":
    print("Güzel ilerliyorsun! O zaman sıradaki hedefin: Batman Beyond")

else:
    print("Hmmm, listemde bu isme göre bir yönlendirme yok. Acaba ismini mi yanlış yazdın?")