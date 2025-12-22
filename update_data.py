import requests
import json
import os

ANA_DOSYA = "depremler.json"
GUNCEL_DOSYA = "son_depremler.json"

def verileri_guncelle():
    print("🚀 Güncelleme robotu başlatıldı...")
    
    # --- 1. MEVCUT ARŞİVİ OKU ---
    mevcut_veri = []
    if os.path.exists(ANA_DOSYA):
        try:
            with open(ANA_DOSYA, "r", encoding="utf-8") as f:
                mevcut_veri = json.load(f)
            print(f"📦 Arşivde {len(mevcut_veri)} kayıt var.")
        except Exception as e:
            print(f"🚨 Dosya okuma hatası: {e}")
            return

    # --- 2. API'DEN VERİ ÇEK ---
    url = "https://api.orhanaydogdu.com.tr/deprem/kandilli/live?limit=500"
    
    yeni_gelenler = []
    try:
        print("🌍 API'ye bağlanılıyor...")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if "result" in data:
                ham_veriler = data["result"]
                
                # --- KRİTİK DÜZELTME BURADA ---
                # API 'date_time' veriyor ama bizim sistem 'date' kullanıyor.
                # Gelen veriyi bizim formatımıza çeviriyoruz.
                for item in ham_veriler:
                    # Eğer 'date_time' varsa onu 'date' olarak kopyala
                    if "date_time" in item:
                        item["date"] = item["date_time"]
                    
                    # Büyüklük Filtresi (3.0 ve üzeri)
                    # Bazen mag str gelebilir, float'a çevirip kontrol edelim
                    try:
                        buyukluk = float(item.get("mag", 0))
                        if buyukluk >= 3.0:
                            yeni_gelenler.append(item)
                    except:
                        # Eğer büyüklük hatalıysa yine de ekle (veri kaybı olmasın)
                        yeni_gelenler.append(item)

                print(f"📡 API'den {len(yeni_gelenler)} adet uygun veri (3.0+) alındı.")
            else:
                print("⚠️ API yanıtında 'result' bulunamadı.")
        else:
            print(f"❌ API Hatası: Kod {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return

    # --- 3. KARŞILAŞTIR VE EKLE ---
    # Benzersizlik kontrolü için ID seti oluştur
    mevcut_id_seti = set()
    for d in mevcut_veri:
        # Eski verilerde 'date' var, yenilerde de artık 'date' var (biz ekledik)
        uid = f"{d.get('date')}_{d.get('title')}"
        mevcut_id_seti.add(uid)

    eklenen_sayisi = 0
    
    # API verilerini tersten (eskiden yeniye) dönerek ekle
    for deprem in reversed(yeni_gelenler):
        uid = f"{deprem.get('date')}_{deprem.get('title')}"
        
        if uid not in mevcut_id_seti:
            mevcut_veri.insert(0, deprem)
            mevcut_id_seti.add(uid)
            eklenen_sayisi += 1

    if eklenen_sayisi > 0:
        print(f"✅ {eklenen_sayisi} YENİ DEPREM ARŞİVE EKLENDİ!")
        
        # --- 4. DOSYALARI KAYDET ---
        try:
            with open(ANA_DOSYA, "w", encoding="utf-8") as f:
                json.dump(mevcut_veri, f, ensure_ascii=False, indent=None)
            
            with open(GUNCEL_DOSYA, "w", encoding="utf-8") as f:
                json.dump(mevcut_veri[:500], f, ensure_ascii=False, indent=None)
                
            print("💾 Dosyalar başarıyla güncellendi.")
        except Exception as e:
            print(f"❌ Yazma hatası: {e}")
    else:
        print("💤 Yeni deprem yok. Arşiv güncel.")

if __name__ == "__main__":
    verileri_guncelle()
