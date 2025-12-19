import requests
import json
import os
from datetime import datetime

# Dosya İsimleri
ANA_DOSYA = "depremler.json"
GUNCEL_DOSYA = "son_depremler.json"

def verileri_guncelle():
    print("Islem basliyor...")
    
    # 1. MEVCUT ARŞİVİ OKU
    if os.path.exists(ANA_DOSYA):
        with open(ANA_DOSYA, "r", encoding="utf-8") as f:
            try:
                mevcut_veri = json.load(f)
            except:
                mevcut_veri = []
    else:
        mevcut_veri = []
    
    print(f"Mevcut veri sayisi: {len(mevcut_veri)}")

    # 2. KANDİLLİ'DEN YENİ VERİLERİ ÇEK
    url = "https://api.orhanaydogdu.com.tr/deprem/kandilli/live"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print("API hatasi!")
            return
        yeni_veriler = response.json()["result"]
    except Exception as e:
        print(f"Hata: {e}")
        return

    # 3. KONTROL VE BİRLEŞTİRME
    # Mevcut verilerin tarihlerini bir kümede (set) tutalım ki hızlı kontrol edelim
    # Not: API tarih formatı "2023.12.18 14:30:00" şeklindedir.
    mevcut_tarihler = {d["date"] for d in mevcut_veri}
    
    eklenen_sayisi = 0
    
    # Yeni gelen listeyi tersten dönüyoruz (Eskiden Yeniye)
    # Böylece listemizin en tepesine (index 0) en son depremi ekleriz.
    for deprem in reversed(yeni_veriler):
        # Sadece 3.0 ve üzerini alalım (Senin tercihin, istersen bu satırı silip hepsini alırsın)
        if deprem["mag"] >= 3.0:
            # Eğer bu tarih bizde yoksa ekle
            if deprem["date"] not in mevcut_tarihler:
                mevcut_veri.insert(0, deprem) # En başa ekle
                mevcut_tarihler.add(deprem["date"])
                eklenen_sayisi += 1

    # 4. KAYDETME
    if eklenen_sayisi > 0:
        print(f"Toplanda {eklenen_sayisi} yeni deprem eklendi.")
        
        # A) Ana Arşivi Kaydet (Yedek)
        with open(ANA_DOSYA, "w", encoding="utf-8") as f:
            json.dump(mevcut_veri, f, ensure_ascii=False, indent=None) # indent=None dosya boyutunu küçültür
            
        # B) Güncel Dosyayı Kaydet (Mobil Uygulama İçin - İlk 100 Veri)
        # Uygulama açılışta sadece bunu çekecek, çok hızlı olacak.
        with open(GUNCEL_DOSYA, "w", encoding="utf-8") as f:
            json.dump(mevcut_veri[:100], f, ensure_ascii=False, indent=None)
            
        print("Dosyalar güncellendi.")
    else:
        print("Yeni deprem bulunamadi, dosyalar degismedi.")

if __name__ == "__main__":
    verileri_guncelle()
