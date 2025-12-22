import requests
import json
import os
import time

# Dosya yolları artık genel. Script neredeyse oraya bakar.
ANA_DOSYA = "depremler.json"
GUNCEL_DOSYA = "son_depremler.json"

def bosluk_doldur_dongulu():
    print("🚑 GELİŞMİŞ Boşluk Doldurma Operasyonu Başladı...")
    print(f"📂 Çalışılan Dosya: {ANA_DOSYA}")
    print("Hedef: 100'er 100'er atlayarak 2000 veri taramak.")

    # 1. MEVCUT ARŞİVİ YÜKLE
    mevcut_veri = []
    if os.path.exists(ANA_DOSYA):
        try:
            with open(ANA_DOSYA, "r", encoding="utf-8") as f:
                mevcut_veri = json.load(f)
            print(f"📦 Mevcut arşivde {len(mevcut_veri)} kayıt var.")
        except Exception as e:
            print(f"🚨 Dosya okuma hatası: {e}")
            return
    else:
        print("🚨 'depremler.json' bulunamadı! Bu scripti json dosyasının yanına koydun mu?")
        return

    # ID Listesi (Hızlı kontrol için)
    mevcut_id_seti = set()
    for d in mevcut_veri:
        # date ve title birleşimiyle ID yapıyoruz
        uid = f"{d.get('date')}_{d.get('title')}"
        mevcut_id_seti.add(uid)

    # 2. DÖNGÜ İLE VERİ ÇEKME (0'dan 2000'e kadar, 100'er adım)
    toplam_yeni_eklenen = 0

    for skip_miktari in range(0, 2000, 100):
        # URL'yi dinamik oluşturuyoruz: limit=100 sabit, skip değişiyor
        url = f"https://api.orhanaydogdu.com.tr/deprem/kandilli/archive?limit=100&skip={skip_miktari}"
        
        print(f"\n🔄 İstek yapılıyor: {skip_miktari} - {skip_miktari + 100} arası...")
        
        try:
            response = requests.get(url, timeout=20)
            data = response.json()
            
            if response.status_code == 200 and "result" in data:
                ham_liste = data["result"]
                gelen_adet = len(ham_liste)
                
                if gelen_adet == 0:
                    print("🛑 Veri bitti, döngü sonlandırılıyor.")
                    break

                sayfa_eklenen = 0
                
                # 3. VERİLERİ İŞLE VE FİLTRELE
                for item in ham_liste:
                    # Tarih Düzeltmesi
                    if "date_time" in item:
                        item["date"] = item["date_time"]
                    
                    # Büyüklük Filtresi (3.0 ve üzeri)
                    try:
                        mag = float(item.get("mag", 0))
                        if mag >= 3.0:
                            # ID Kontrolü (Bizde var mı?)
                            uid = f"{item.get('date')}_{item.get('title')}"
                            
                            if uid not in mevcut_id_seti:
                                # Yoksa BAŞA ekle
                                mevcut_veri.insert(0, item)
                                mevcut_id_seti.add(uid)
                                sayfa_eklenen += 1
                                toplam_yeni_eklenen += 1
                                print(f"   ✅ BULUNDU: {item['date']} - {item['title']}")
                    except:
                        continue
                
                if sayfa_eklenen > 0:
                    print(f"   ➡️ Bu sayfadan {sayfa_eklenen} yeni deprem eklendi.")
                else:
                    print("   💤 Bu sayfadakilerin hepsi zaten var.")
                
                # API'yi yormamak için 1 saniye bekle
                time.sleep(1)

            else:
                print("❌ API hatası veya boş veri.")
                
        except Exception as e:
            print(f"❌ Bağlantı hatası: {e}")
            break

    # 4. KAYDETME İŞLEMİ (Döngü bitince yapılır)
    if toplam_yeni_eklenen > 0:
        print(f"\n🎉 SONUÇ: Toplam {toplam_yeni_eklenen} adet EKSİK deprem kurtarıldı!")
        
        try:
            # Büyük dosya
            with open(ANA_DOSYA, "w", encoding="utf-8") as f:
                json.dump(mevcut_veri, f, ensure_ascii=False, indent=None)
            
            # Küçük dosya
            with open(GUNCEL_DOSYA, "w", encoding="utf-8") as f:
                json.dump(mevcut_veri[:500], f, ensure_ascii=False, indent=None)
                
            print("💾 Dosyalar başarıyla kaydedildi.")
        except Exception as e:
            print(f"❌ Yazma hatası: {e}")
    else:
        print("\n💤 Hiç yeni veri bulunamadı. Arşiv zaten eksiksiz.")

if __name__ == "__main__":
    bosluk_doldur_dongulu()
