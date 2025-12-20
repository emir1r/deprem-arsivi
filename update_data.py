import requests
import json
import os
import sys # Hata basmak için gerekli

ANA_DOSYA = "depremler.json"
GUNCEL_DOSYA = "son_depremler.json"

def verileri_guncelle():
    print("🚀 Güncelleme robotu çalıştı...")
    
    # --- ADIM 1: BÜYÜK DOSYAYI OKU (HATA VARSA GÖSTER) ---
    mevcut_veri = []
    if os.path.exists(ANA_DOSYA):
        try:
            with open(ANA_DOSYA, "r", encoding="utf-8") as f:
                mevcut_veri = json.load(f)
            print(f"📦 Arşiv dosyası okundu. İçinde {len(mevcut_veri)} adet kayıt var.")
        except Exception as e:
            print(f"🚨 KRİTİK HATA: Büyük dosya okunurken hata oluştu!")
            print(f"Hata Detayı: {e}")
            # Hata varsa işlemi durdurmayalım ama bilelim ki arşiv boş geldi
            mevcut_veri = []
    else:
        print("⚠️ UYARI: 'depremler.json' dosyası yerinde yok!")

    # --- ADIM 2: CANLI VERİ ÇEK ---
    url = "https://api.orhanaydogdu.com.tr/deprem/kandilli/live?limit=500"
    yeni_veriler = []
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if "result" in data:
                yeni_veriler = data["result"]
                print(f"📡 Kandilli'den {len(yeni_veriler)} adet canlı veri geldi.")
    except Exception as e:
        print(f"❌ API Hatası: {e}")

    # --- ADIM 3: BİRLEŞTİR ---
    # Tarihleri referans alarak tekrarı önle
    mevcut_tarihler = {d.get("date") for d in mevcut_veri if d.get("date")}
    eklenen_sayisi = 0
    
    # Yeni verileri eskisinin üzerine ekle
    for deprem in reversed(yeni_veriler):
        tarih = deprem.get("date")
        if tarih and tarih not in mevcut_tarihler:
            mevcut_veri.insert(0, deprem)
            mevcut_tarihler.add(tarih)
            eklenen_sayisi += 1

    print(f"➕ Toplam {eklenen_sayisi} adet yeni deprem arşive eklendi.")
    print(f"📊 Şu an elimizdeki toplam veri sayısı: {len(mevcut_veri)}")

    # --- ADIM 4: KAYDET (LOGLU) ---
    try:
        # A) Büyük Arşiv
        with open(ANA_DOSYA, "w", encoding="utf-8") as f:
            json.dump(mevcut_veri, f, ensure_ascii=False, indent=None)
            
        # B) Küçük Vitrin (500 ADET)
        vitrin_verisi = mevcut_veri[:500]
        with open(GUNCEL_DOSYA, "w", encoding="utf-8") as f:
            json.dump(vitrin_verisi, f, ensure_ascii=False, indent=None)
            
        print(f"💾 KAYIT BAŞARILI: 'son_depremler.json' dosyasına {len(vitrin_verisi)} adet veri yazıldı.")
    
    except Exception as e:
        print(f"❌ DOSYA YAZMA HATASI: {e}")

if __name__ == "__main__":
    verileri_guncelle()
