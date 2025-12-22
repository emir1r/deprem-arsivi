import requests
import json
import os

ANA_DOSYA = "depremler.json"

def bosluk_doldur():
    print("🚑 Boşluk Doldurma Operasyonu Başladı...")

    # 1. MEVCUT ARŞİVİ YÜKLE
    mevcut_veri = []
    if os.path.exists(ANA_DOSYA):
        with open(ANA_DOSYA, "r", encoding="utf-8") as f:
            mevcut_veri = json.load(f)
        print(f"📦 Mevcut arşivde {len(mevcut_veri)} kayıt var.")
    else:
        print("🚨 Arşiv dosyası bulunamadı!")
        return

    # 2. API'DEN GEÇMİŞE YÖNELİK VERİ ÇEK (ARCHIVE ENDPOINT)
    # limit=2000 diyerek son bir haftayı garantiye alıyoruz
    url = "https://api.orhanaydogdu.com.tr/deprem/kandilli/archive?limit=2000"
    
    print(f"🌍 API'ye bağlanılıyor: {url}")
    
    try:
        response = requests.get(url, timeout=60) # Süreyi uzattık
        data = response.json()
        
        if response.status_code == 200 and "result" in data:
            ham_liste = data["result"]
            print(f"📊 API'den TOPLAM {len(ham_liste)} adet ham veri geldi.") 
            # (Burada 100 yazıyorsa API limitini zorlamıyor demektir, 1000+ görmeliyiz)

            uygun_adaylar = []
            
            # 3. VERİLERİ DÜZENLE VE FİLTRELE
            for item in ham_liste:
                # Tarih düzeltmesi (date_time -> date)
                if "date_time" in item:
                    item["date"] = item["date_time"]
                
                # Büyüklük Filtresi (3.0+)
                try:
                    mag = float(item.get("mag", 0))
                    if mag >= 3.0:
                        uygun_adaylar.append(item)
                except:
                    continue

            print(f"mag >= 3.0 filtresinden geçen aday sayısı: {len(uygun_adaylar)}")

            # 4. KIYASLA VE EKLE
            # Arşivdeki ID'leri bir sete atalım (Hız için)
            mevcut_id_seti = set()
            for d in mevcut_veri:
                uid = f"{d.get('date')}_{d.get('title')}"
                mevcut_id_seti.add(uid)

            eklenenler = 0
            # Adayları tersten (eskiden yeniye) tarayıp ekle
            for aday in reversed(uygun_adaylar):
                uid = f"{aday.get('date')}_{aday.get('title')}"
                
                if uid not in mevcut_id_seti:
                    # BAŞA EKLE
                    mevcut_veri.insert(0, aday)
                    mevcut_id_seti.add(uid)
                    eklenenler += 1
                    # Merak ediyorsan ekleneni yazdır:
                    # print(f"   ➕ Eklendi: {aday['date']} - {aday['title']}")

            if eklenenler > 0:
                print(f"✅ TOPLAM {eklenenler} ADET KAYIP DEPREM ARŞİVE EKLENDİ!")
                
                # KAYDET
                with open(ANA_DOSYA, "w", encoding="utf-8") as f:
                    json.dump(mevcut_veri, f, ensure_ascii=False, indent=None)
                
                # Küçük dosyayı da güncelle
                with open("son_depremler.json", "w", encoding="utf-8") as f:
                    json.dump(mevcut_veri[:500], f, ensure_ascii=False, indent=None)
                    
                print("💾 Dosyalar kaydedildi. Şimdi GitHub'a push edebilirsin.")
            else:
                print("💤 Eksik veri bulunamadı. Arşiv ile API birebir örtüşüyor.")

        else:
            print("❌ API yanıtı hatalı.")

    except Exception as e:
        print(f"❌ Hata oluştu: {e}")

if __name__ == "__main__":
    bosluk_doldur()
