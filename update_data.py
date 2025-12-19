import requests
import json
import os

# Dosya İsimleri
ANA_DOSYA = "depremler.json"
GUNCEL_DOSYA = "son_depremler.json"

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

    # 2. KANDİLLİ'DEN CANLI VERİ ÇEK
    url = "https://api.orhanaydogdu.com.tr/deprem/kandilli/live?limit=500"
    yeni_veriler = []
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            # API bazen result döndürmez, kontrol edelim
            if "result" in data:
                yeni_veriler = data["result"]
                print(f"📡 Kandilli'den {len(yeni_veriler)} adet canlı veri çekildi.")
            else:
                print("⚠️ API yanıtında 'result' bulunamadı.")
        else:
            print(f"❌ API Hatası: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return

    # 3. KONTROL VE BİRLEŞTİRME
    # Hata veren kısım burasıydı. Artık .get() kullanarak güvenli hale getiriyoruz.
    # Eğer "date" yoksa o veriyi yoksayacağız.
    mevcut_tarihler = set()
    for d in mevcut_veri:
        tarih = d.get("date") # Varsa al, yoksa None ver
        if tarih:
            mevcut_tarihler.add(tarih)
    
    eklenen_sayisi = 0
    
    # Yeni gelenleri işle
    for deprem in reversed(yeni_veriler):
        yeni_tarih = deprem.get("date")
        
        # Eğer tarih bilgisi yoksa veya zaten bizde varsa atla
        if not yeni_tarih or yeni_tarih in mevcut_tarihler:
            continue
            
        # Eğer veri geçerliyse ekle
        mevcut_veri.insert(0, deprem)
        mevcut_tarihler.add(yeni_tarih)
        eklenen_sayisi += 1

    # 4. KAYDETME
    if eklenen_sayisi > 0 or not os.path.exists(GUNCEL_DOSYA):
        print(f"✅ {eklenen_sayisi} yeni deprem arşive eklendi.")
        
        try:
            # A) Büyük Arşivi Güncelle
            with open(ANA_DOSYA, "w", encoding="utf-8") as f:
                json.dump(mevcut_veri, f, ensure_ascii=False, indent=None)
                
            # B) Küçük Dosyayı Oluştur (Mobil Uygulama İçin - İlk 100)
            with open(GUNCEL_DOSYA, "w", encoding="utf-8") as f:
                json.dump(mevcut_veri[:100], f, ensure_ascii=False, indent=None)
                
            print("💾 Dosyalar başarıyla kaydedildi.")
        except Exception as e:
            print(f"❌ Kaydetme hatası: {e}")
    else:
        print("💤 Yeni deprem yok, dosyalar güncel.")

if __name__ == "__main__":
    verileri_guncelle()
