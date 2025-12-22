import requests
import json
import os

# GitHub Actions ortamı için ayarlar
ANA_DOSYA = "depremler.json"
GUNCEL_DOSYA = "son_depremler.json"

def verileri_guncelle():
    print("🤖 Günlük Robot Çalıştı (Normal Mod)...")
    
    # 1. MEVCUT DOSYAYI OKU
    mevcut_veri = []
    if os.path.exists(ANA_DOSYA):
        try:
            with open(ANA_DOSYA, "r", encoding="utf-8") as f:
                mevcut_veri = json.load(f)
            # Logu kirletmemek için yazdırmıyorum, istersen açabilirsin:
            # print(f"📦 Arşivde {len(mevcut_veri)} kayıt var.")
        except Exception as e:
            print(f"🚨 Okuma hatası: {e}")
            # Dosya bozuksa boş liste ile devam et
            mevcut_veri = []
    
    # 2. API'DEN CANLI VERİ ÇEK (Sadece son 500)
    url = "https://api.orhanaydogdu.com.tr/deprem/kandilli/live?limit=500"
    
    yeni_gelenler = []
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if "result" in data:
                for item in data["result"]:
                    # --- İSİM DÜZELTME ---
                    # API 'date_time' verirse 'date' olarak kaydediyoruz
                    if "date_time" in item:
                        item["date"] = item["date_time"]
                    
                    # 3.0 ve Üzeri Filtresi
                    try:
                        mag = float(item.get("mag", 0))
                        if mag >= 3.0:
                            yeni_gelenler.append(item)
                    except:
                        continue
            else:
                print("⚠️ API yanıtında veri yok.")
        else:
            print(f"❌ API Hatası: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return

    # 3. KIYASLA VE BİRLEŞTİR
    # Mevcut verilerin ID'lerini bir kümeye (set) atıyoruz ki hızlı bulalım
    mevcut_id_seti = set()
    for d in mevcut_veri:
        uid = f"{d.get('date')}_{d.get('title')}"
        mevcut_id_seti.add(uid)

    eklenen = 0
    # Yeni gelenleri tersten (eskiden yeniye) tarayıp ekle
    # Böylece listenin en başına en yenisi gelir
    for deprem in reversed(yeni_gelenler):
        uid = f"{deprem.get('date')}_{deprem.get('title')}"
        
        if uid not in mevcut_id_seti:
            mevcut_veri.insert(0, deprem) # En başa ekle
            mevcut_id_seti.add(uid)
            eklenen += 1

    # 4. KAYDET (YAML dosyası commit işlemini yapacak)
    if eklenen > 0:
        print(f"✅ {eklenen} YENİ DEPREM EKLENDİ.")
        
        try:
            # Ana arşiv dosyası
            with open(ANA_DOSYA, "w", encoding="utf-8") as f:
                json.dump(mevcut_veri, f, ensure_ascii=False, indent=None)
            
            # Uygulama için küçük dosya (Son 500)
            with open(GUNCEL_DOSYA, "w", encoding="utf-8") as f:
                json.dump(mevcut_veri[:500], f, ensure_ascii=False, indent=None)
                
            print("💾 Dosyalar güncellendi.")
        except Exception as e:
            print(f"❌ Yazma hatası: {e}")
            exit(1) # Hata olursa Actions başarısız görünsün
    else:
        print("💤 Yeni veri yok. Dosyalar değiştirilmedi.")

if __name__ == "__main__":
    verileri_guncelle()
