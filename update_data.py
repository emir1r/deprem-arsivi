import requests
import json
import os

# Dosya İsimleri
ANA_DOSYA = "depremler.json"       # Senin yüklediğin büyük dosya
GUNCEL_DOSYA = "son_depremler.json" # Uygulama için küçük dosya

def verileri_guncelle():
    print("🚀 Güncelleme robotu çalıştı...")
    
    # 1. MEVCUT BÜYÜK ARŞİVİ OKU
    mevcut_veri = []
    if os.path.exists(ANA_DOSYA):
        try:
            with open(ANA_DOSYA, "r", encoding="utf-8") as f:
                mevcut_veri = json.load(f)
            print(f"📦 Mevcut arşiv yüklendi: {len(mevcut_veri)} adet kayıt.")
        except Exception as e:
            print(f"⚠️ Dosya okuma hatası: {e}")
            mevcut_veri = []
    else:
        print("⚠️ Ana dosya bulunamadı! Sıfırdan başlanıyor.")

    # 2. KANDİLLİ'DEN CANLI VERİ ÇEK (Son 500)
    url = "https://api.orhanaydogdu.com.tr/deprem/kandilli/live?limit=500"
    yeni_veriler = []
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            yeni_veriler = response.json()["result"]
            print(f"📡 Kandilli'den {len(yeni_veriler)} adet canlı veri çekildi.")
        else:
            print("❌ API Hatası!")
            return
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return

    # 3. KONTROL VE BİRLEŞTİRME
    # Hız için tarihleri bir kümeye (set) alıyoruz
    mevcut_tarihler = {d["date"] for d in mevcut_veri}
    
    eklenen_sayisi = 0
    
    # Yeni gelenleri tersten (eskiden yeniye) tarıyoruz ki sırayla ekleyelim
    for deprem in reversed(yeni_veriler):
        # Büyüklük filtresi (İstersen 3.0 yapabilirsin, şimdilik hepsini alalım)
        # Veritabanımızda bu tarih yoksa ekle
        if deprem["date"] not in mevcut_tarihler:
            mevcut_veri.insert(0, deprem) # En tepeye ekle
            mevcut_tarihler.add(deprem["date"])
            eklenen_sayisi += 1

    # 4. KAYDETME (Sadece yeni veri varsa veya küçük dosya yoksa)
    if eklenen_sayisi > 0 or not os.path.exists(GUNCEL_DOSYA):
        print(f"✅ {eklenen_sayisi} yeni deprem arşive eklendi.")
        
        # A) Büyük Arşivi Güncelle
        with open(ANA_DOSYA, "w", encoding="utf-8") as f:
            # indent=None dosya boyutunu %30 küçültür (Minified JSON)
            json.dump(mevcut_veri, f, ensure_ascii=False, indent=None)
            
        # B) Küçük Dosyayı Oluştur (Mobil Uygulama Açılışı İçin - İlk 100)
        with open(GUNCEL_DOSYA, "w", encoding="utf-8") as f:
            json.dump(mevcut_veri[:100], f, ensure_ascii=False, indent=None)
            
        print("💾 Dosyalar başarıyla kaydedildi.")
    else:
        print("💤 Yeni deprem yok, dosyalar güncel.")

if __name__ == "__main__":
    verileri_guncelle()
