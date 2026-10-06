#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite ile Quiz Veri Tabanı - Seed (Veri Doldurma) Betiği
Bu betik 60 kullanıcı, 5 oturum ve 110 Benzersiz Soru kaydını ilişkili tablolarla birlikte oluşturur.
"""

import os
import sys
import random
import sqlite3
from datetime import datetime, timedelta

# Windows konsol kodlamasını UTF-8 yap
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

DB_PATH = os.path.join(os.path.dirname(__file__), "quiz.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

# Örnek İsimler & Soyisimler
FIRST_NAMES = [
    "Ahmet", "Mehmet", "Ayşe", "Fatma", "Ali", "Zeynep", "Mustafa", "Elif", "Can", "Burak",
    "Ceren", "Deniz", "Ege", "Emre", "Gamze", "Hakan", "İrem", "Kaan", "Leyla", "Mert",
    "Nisa", "Oğuz", "Ömer", "Pınar", "Selin", "Serkan", "Tarık", "Umut", "Volkan", "Yağmur",
    "Yiğit", "Aslı", "Berk", "Bora", "Buse", "Cem", "Defne", "Eda", "Erhan", "Gizem",
    "Gökhan", "Hande", "Harun", "İlker", "Kadir", "Melis", "Murat", "Naz", "Onur", "Ozan",
    "Pelin", "Rıza", "Seda", "Sinan", "Tuğba", "Turgut", "Uğur", "Yasemin", "Yunus", "Zehra"
]

LAST_NAMES = [
    "Yılmaz", "Kaya", "Demir", "Şahin", "Çelik", "Yıldız", "Yıldırım", "Öztürk", "Aydın", "Özdemir",
    "Arslan", "Doğan", "Kılıç", "Aslan", "Çetin", "Kara", "Koç", "Kurt", "Özcan", "Şimşek",
    "Çakır", "Erdoğan", "Yalçın", "Korkmaz", "Yavuz", "Şen", "Aktaş", "Güneş", "Ünal", "Bozkurt"
]

CATEGORIES = ["SQL Temelleri", "Veri Tabanı Tasarımı", "İndeksler & Performans", "İlişkisel Cebir", "SQLite & PostgreSQL"]
DIFFICULTIES = ["kolay", "orta", "zor"]

# 110 Adet Tamamen Benzersiz Veritabanı ve Yazılım Sorusu Bankası
RAW_QUESTIONS = [
    ("SQL'de tablodaki verileri güncellemek için hangi komut kullanılır?", ["UPDATE", "MODIFY", "ALTER", "CHANGE"], 0, "SQL Temelleri"),
    ("Bir birincil anahtarda (Primary Key) hangisi doğru olamaz?", ["Benzersiz olması", "NULL değer içerebilmesi", "Tekil indeks oluşturması", "Tabloda en fazla 1 adet tanımlanması"], 1, "Veri Tabanı Tasarımı"),
    ("Yabancı Anahtar (Foreign Key) ilişkisinin temel amacı nedir?", ["Sorgu hızını artırmak", "Referansel veri bütünlüğünü sağlamak", "Tabloyu şifrelemek", "Veri boyutunu küçültmek"], 1, "Veri Tabanı Tasarımı"),
    ("SQLite'ta yabancı anahtar denetimini aktif etmek için kullanılan pragma komutu hangisidir?", ["PRAGMA foreign_keys = ON;", "SET FOREIGN_KEY_CHECKS = 1;", "ENABLE FOREIGN KEYS;", "PRAGMA fk_check = TRUE;"], 0, "SQLite & PostgreSQL"),
    ("1NF (Birinci Normal Form) kuralı aşağıdakilerden hangisini gerektirir?", ["Tüm niteliklerin atomik (bölünemez) olması", "Kısmi bağımlılıkların kaldırılması", "Geçişli bağımlılıkların kaldırılması", "Her tablonun en az 3 ikincil indeksi olması"], 0, "Veri Tabanı Tasarımı"),
    ("İkinci Normal Form (2NF) hangisini ortadan kaldırmayı hedefler?", ["Atomik olmayan değerleri", "Kısmi (Partial) bağımlılıkları", "Geçişli (Transitive) bağımlılıkları", "Çok değerli bağımlılıkları"], 1, "Veri Tabanı Tasarımı"),
    ("Üçüncü Normal Form (3NF) hangisini ortadan kaldırmayı hedefler?", ["Geçişli (Transitive) fonksiyonel bağımlılıkları", "Birincil anahtarları", "Yabancı anahtarları", "NULL değerlerini"], 0, "Veri Tabanı Tasarımı"),
    ("ACID prensiplerinde 'A' harfi hangi kavramı temsil eder?", ["Atomicity (Bütünlük/Bölünemezlik)", "Accuracy (Doğruluk)", "Availability (Erişilebilirlik)", "Authenticity (Kimlik Doğrulama)"], 0, "Veri Tabanı Tasarımı"),
    ("ACID prensiplerinde 'C' harfi ne anlama gelir?", ["Consistency (Tutarlılık)", "Concurrency (Eşzamanlılık)", "Compatibility (Uyumluluk)", "Capacity (Kapasite)"], 0, "Veri Tabanı Tasarımı"),
    ("ACID prensiplerinde 'I' harfi hangi kavramı temsil eder?", ["Isolation (Yalıtım/İzolasyon)", "Integrity (Bütünlük)", "Index (İndeks)", "Inheritance (Kalıtım)"], 0, "Veri Tabanı Tasarımı"),
    ("ACID prensiplerinde 'D' harfi ne anlama gelir?", ["Durability (Kalıcılık/Dayanıklılık)", "Dependability (Güvenilirlik)", "Distributed (Dağıtık)", "Decomposition (Ayrıştırma)"], 0, "Veri Tabanı Tasarımı"),
    ("İki tablonun kesişimini alan ve sadece eşleşen satırları getiren JOIN türü hangisidir?", ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"], 0, "SQL Temelleri"),
    ("Sol tablodaki tüm satırları ve sağ tablodan eşleşen satırları getiren JOIN türü hangisidir?", ["LEFT JOIN (veya LEFT OUTER JOIN)", "INNER JOIN", "CROSS JOIN", "SELF JOIN"], 0, "SQL Temelleri"),
    ("SQLite veri tabanında otomatik artan birincil anahtar sütunu nasıl tanımlanır?", ["INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY", "INT AUTO_INCREMENT PRIMARY KEY", "BIGINT IDENTITY(1,1)"], 0, "SQLite & PostgreSQL"),
    ("SQL'de tekrarlayan satırları teke indirmek için hangi sözcük kullanılır?", ["DISTINCT", "UNIQUE", "GROUP BY", "SINGLE"], 0, "SQL Temelleri"),
    ("HAVING yan tümcesinin WHERE yan tümcesinden temel farkı nedir?", ["HAVING gruplanmış (GROUP BY) veriler üzerinde filtreleme yapar", "WHERE daha hızlı çalışır", "HAVING indeks kullanamaz", "WHERE sadece sayılar için kullanılır"], 0, "SQL Temelleri"),
    ("Tablodan bir sütunu tamamen kaldırmak için hangi SQL ifadesi kullanılır?", ["ALTER TABLE ... DROP COLUMN", "DELETE COLUMN ... FROM", "REMOVE COLUMN ... FROM", "DROP ATTRIBUTE ... FROM"], 0, "SQL Temelleri"),
    ("Veri tabanında arama performansını hızlandırmak için kullanılan yapı hangisidir?", ["INDEX (İndeks)", "VIEW (Görünüm)", "TRIGGER (Tetikleyici)", "TRANSACTION (İşlem)"], 0, "İndeksler & Performans"),
    ("B-Tree indeksi ile ilgili aşağıdakilerden hangisi doğrudur?", ["Arama, ekleme ve silme işlemlerini O(log N) karmaşıklığında gerçekleştirir", "Yalnızca metin alanlarında çalışır", "FOREIGN KEY tanımlamasını zorunlu kılar", "Veriyi diskte rastgele saklar"], 0, "İndeksler & Performans"),
    ("Tabloda aynı değere sahip birden fazla kayıt girilmesini engelleyen kısıt (constraint) hangisidir?", ["UNIQUE", "CHECK", "FOREIGN KEY", "DEFAULT"], 0, "Veri Tabanı Tasarımı"),
    ("Bir sütuna girilecek değerlerin belirli bir aralıkta olmasını sağlayan kısıt hangisidir?", ["CHECK", "RANGE", "LIMIT", "CONSTRAINT_VALUE"], 0, "Veri Tabanı Tasarımı"),
    ("SQL'de tablo silmek için hangi komut kullanılır?", ["DROP TABLE", "DELETE TABLE", "TRUNCATE TABLE", "REMOVE TABLE"], 0, "SQL Temelleri"),
    ("Tablo yapısını değiştirmeden içindeki tüm verileri silen komut hangisidir?", ["DELETE FROM tablo_adi;", "DROP TABLE tablo_adi;", "ALTER TABLE tablo_adi CLEAR;", "UPDATE tablo_adi SET NULL;"], 0, "SQL Temelleri"),
    ("Geçici veya sanal tablolar oluşturmak için kullanılan SQL yapısı hangisidir?", ["VIEW", "INDEX", "SCHEMA", "PROCEDURE"], 0, "SQL Temelleri"),
    ("Veri tabanında belirli bir olay (INSERT, UPDATE, DELETE) gerçekleştiğinde otomatik çalışan yapı nedir?", ["TRIGGER (Tetikleyici)", "FUNCTION", "INDEX", "SEQUENCE"], 0, "Veri Tabanı Tasarımı"),
    ("PostgreSQL ile SQLite arasındaki en belirgin farklardan biri nedir?", ["PostgreSQL istemci-sunucu mimarisindedir, SQLite ise dosya tabanlı gömülü kütüphanedir", "SQLite SQL standartlarını desteklemez", "PostgreSQL indeks desteklemez", "SQLite çok kullanıcılı devasa sunucularda çalışmak için tasarlanmıştır"], 0, "SQLite & PostgreSQL"),
    ("Relational Algebra'da Selection (Seçme) işlemi hangi sembolle gösterilir?", ["Sigma (σ)", "Pi (π)", "Rho (ρ)", "Gamma (γ)"], 0, "İlişkisel Cebir"),
    ("Relational Algebra'da Projection (İzdüşüm) işlemi hangi sembolle gösterilir?", ["Pi (π)", "Sigma (σ)", "Theta (θ)", "Delta (δ)"], 0, "İlişkisel Cebir"),
    ("SQLite varsayılan olarak veriyi hangi formatta saklar?", ["Tek bir disk dosyasında (.db / .sqlite)", "Her tablo için ayrı klasörde", "RAM bellekte geçici olarak", "JSON formatında sunucuda"], 0, "SQLite & PostgreSQL"),
    ("SQL'de gruplama yapmak için hangi yan tümce kullanılır?", ["GROUP BY", "ORDER BY", "CLUSTER BY", "PARTITION BY"], 0, "SQL Temelleri"),
    ("PostgreSQL'de JSONB veritipi için aşağıdakilerden hangisi doğrudur?", ["İndekslenebilir ikili (binary) JSON formatıdır", "Sadece DDL kodlarını tutar", "Grafik çizimi içindir", "Metin dosyasıdır"], 0, "SQLite & PostgreSQL"),
    ("SQL 'LIKE %abc' araması neden indeksi etkili kullanamaz?", ["Joker karakter (%) başta olduğu için B-Tree indeks arama ağacı taranamaz", "LIKE ifadesi indeksleri tamamen iptal eder", "Sadece rakamlarda indeks kullanılır", "SQLite LIKE komutunu desteklemez"], 0, "İndeksler & Performans"),
    ("Denormalizasyon (Denormalization) ne zaman tercih edilir?", ["Okuma (SELECT) performansını artırmak için veri tekrarı göze alındığında", "Veri tabanı alanından tasarruf etmek için", "1NF kuralını bozmak için", "Yabancı anahtarları silmek için"], 0, "Veri Tabanı Tasarımı"),
    ("TRANSACTION işleminde ROLLBACK komutunun görevi nedir?", ["Yapılan değişiklikleri geri alarak veri tabanını önceki güvenli duruma getirir", "İşlemi onaylayıp diske yazar", "Tabloyu tamamen siler", "İndeksleri yeniden oluşturur"], 0, "Veri Tabanı Tasarımı"),
    ("COMMIT komutunun işlevi nedir?", ["Transaction içindeki değişiklikleri kalıcı olarak kaydeder", "Transaction'ı iptal eder", "Bağlantıyı koparır", "Kullanıcıyı sistemden çıkarır"], 0, "Veri Tabanı Tasarımı"),
    ("Kayıtların sıralanması için hangi sözcük kullanılır?", ["ORDER BY", "SORT BY", "ARRANGE BY", "GROUP BY"], 0, "SQL Temelleri"),
    ("SQL'de NULL değer kontrolü nasıl yapılır?", ["IS NULL veya IS NOT NULL ile", "= NULL veya != NULL ile", "NULL() fonksiyonu ile", "EXISTS NULL ile"], 0, "SQL Temelleri"),
    ("Bir tabloda birden fazla sütunun birleşimiyle oluşturulan birincil anahtara ne denir?", ["Bileşik Anahtar (Composite Key)", "Yabancı Anahtar (Foreign Key)", "Aday Anahtar (Candidate Key)", "Süper Anahtar (Super Key)"], 0, "Veri Tabanı Tasarımı"),
    ("Aday Anahtar (Candidate Key) nedir?", ["Birincil anahtar olmaya aday benzersiz nitelik veya nitelik kümesidir", "Yalnızca dış tablodan gelen anahtardır", "Geçici olarak oluşturulan indekstir", "Rastgele üretilen kimlik numarasıdır"], 0, "Veri Tabanı Tasarımı"),
    ("Surrogate Key (Yapay Anahtar) kullanımının avantajı nedir?", ["İş mantığından bağımsız, basit ve sabit boyutlu (örn. AUTOINCREMENT ID) bir anahtar sağlar", "Veri tabanını şifreler", "İlişkileri kaldırır", "Tablo boyutunu sıfırlar"], 0, "Veri Tabanı Tasarımı"),
    ("SQL SELECT COUNT(*) ifadesi ile ilgili aşağıdakilerden hangisi doğrudur?", ["Tablodaki NULL dahil tüm satırların sayısını döndürür", "Yalnızca NULL olmayan değerleri sayar", "Tablodaki sütun sayısını verir", "İndeks bulunmuyorsa hata verir"], 0, "SQL Temelleri"),
    ("Relational Algebra'da Cartesian Product (Kartezyen Çarpım) hangi sembolle gösterilir?", ["X (Çarpı)", "U (Birleşim)", "∩ (Kesişim)", "- (Fark)"], 0, "İlişkisel Cebir"),
    ("Relational Algebra'da Natural Join işlemi hangisini temsil eder?", ["Ortak nitelikler üzerinden eşitlik sağlayan birleştirme", "Tüm satırların rastgele eşleşmesi", "Sadece sol tablonun kopyalanması", "Küme farkı alınması"], 0, "İlişkisel Cebir"),
    ("SQL'de UNION operatörü ile UNION ALL arasındaki temel fark nedir?", ["UNION tekrarlayan kayıtları ayıklar, UNION ALL tümünü getirir", "UNION ALL daha yavaştır", "UNION sadece sayılarda çalışır", "Fark yoktur"], 0, "SQL Temelleri"),
    ("SQL'de EXISTS yan tümcesinin kullanım amacı nedir?", ["Bir alt sorgunun (subquery) herhangi bir satır döndürüp döndürmediğini kontrol etmek", "Tablonun varlığını doğrulamak", "NULL değerleri temizlemek", "İndeks oluşturmak"], 0, "SQL Temelleri"),
    ("SQLite'ta varsayılan veri tipi eğilimi (Type Affinity) mantığı nedir?", ["Kolon veri tipine sıkı sıkıya bağlı kalmadan verinin değerine göre depolama esnekliği sağlar", "Verileri şifreler", "Sadece INT kabul eder", "Veri yazımını engeller"], 0, "SQLite & PostgreSQL"),
    ("PostgreSQL'de SERIAL veri tipi ne anlama gelir?", ["Otomatik artan (Auto-increment) birincil anahtar oluşturmak için kısayol tiptir", "Serileştirilmiş metin tutar", "JSON nesnesidir", "Sadece 1 ile 100 arası tamsayı kabul eder"], 0, "SQLite & PostgreSQL"),
    ("Veri tabanında İzolasyon (Isolation) seviyelerinden Read Uncommitted neye sebep olabilir?", ["Dirty Read (Kirli Okuma)", "Kesin tutarlılık", "Deadlock engelleme", "İndeks kaybı"], 0, "Veri Tabanı Tasarımı"),
    ("Phantom Read (Hayalet Okuma) durumu ne zaman ortaya çıkar?", ["Bir transaction çalışırken başka bir işlem yeni satır ekleyip commit ettiğinde", "Tablo silindiğinde", "İndeks bozulduğunda", "RAM dolduğunda"], 0, "Veri Tabanı Tasarımı"),
    ("SQLite'ta WAL (Write-Ahead Logging) modunun ana avantajı nedir?", ["Okuma ve yazma işlemlerinin birbirini bloklamadan eşzamanlı yapılabilmesi", "Tabloyu küçültmesi", "Şifreleme yapması", "Sadece RAM'de çalışması"], 0, "SQLite & PostgreSQL"),
    ("SQL COALESCE(a, b, c) fonksiyonu nasıl çalışır?", ["Parametreler arasındaki İLK NULL OLMAYAN değeri döndürür", "Tüm parametreleri toplar", "Parametreleri ortalar", "Hata verirse b'yi döner"], 0, "SQL Temelleri"),
    ("SQL NULLIF(exp1, exp2) fonksiyonu ne zaman NULL döndürür?", ["exp1 ile exp2 birbirine EŞİT olduğunda", "exp1 NULL olduğunda", "exp2 sıfır olduğunda", "Her zaman"], 0, "SQL Temelleri"),
    ("PostgreSQL'de EXPLAIN ANALYZE komutu ne işe yarar?", ["Sorgunun sorgu planını ve gerçek çalışma süresini detaylı raporlar", "Tabloyu analiz edip siler", "İndeksleri siler", "Yedek alır"], 0, "SQLite & PostgreSQL"),
    ("Composite Index (Bileşik İndeks) ne zaman etkili kullanılır?", ["Sorgunun WHERE yan tümcesinde indeksin ilk sütunu yer aldığında", "Rastgele sütunlarda", "Sadece tek sütun aramalarında", "DELETE işlemlerinde"], 0, "İndeksler & Performans"),
    ("Covering Index (Kapsayan İndeks) kavramı nedir?", ["Sorguda istenen tüm sütunların indekste bulunup tabloya gitmeden sonucun dönmesi", "Tüm tabloyu kaplayan indeks", "Gizli indeks", "Geçici indeks"], 0, "İndeksler & Performans"),
    ("SQL DDL (Data Definition Language) komutlarına hangisi örnektir?", ["CREATE TABLE", "INSERT INTO", "UPDATE", "SELECT"], 0, "SQL Temelleri"),
    ("SQL DML (Data Manipulation Language) komutlarına hangisi örnektir?", ["INSERT INTO", "CREATE TABLE", "DROP TABLE", "ALTER TABLE"], 0, "SQL Temelleri"),
    ("SQL DCL (Data Control Language) komutlarına hangisi örnektir?", ["GRANT ve REVOKE", "SELECT ve WHERE", "CREATE ve DROP", "COMMIT ve ROLLBACK"], 0, "SQL Temelleri"),
    ("SQL TCL (Transaction Control Language) komutlarına hangisi örnektir?", ["COMMIT ve ROLLBACK", "INSERT ve UPDATE", "GRANT ve REVOKE", "CREATE ve ALTER"], 0, "SQL Temelleri"),
    ("Cascade Delete (ON DELETE CASCADE) seçeneği ne yapar?", ["Ana tablodaki kayıt silindiğinde ona bağlı yabancı anahtarlı alt kayıtları da otomatik siler", "Silmeyi engeller", "Silinen kaydı NULL yapar", "Hata fırlatır"], 0, "Veri Tabanı Tasarımı"),
    ("ON DELETE SET NULL seçeneği ne yapar?", ["Ana kayıt silindiğinde alt tablodaki yabancı anahtar alanını NULL yapar", "Alt kaydı siler", "Hata verir", "İşlemi durdurur"], 0, "Veri Tabanı Tasarımı"),
    ("Foreign Key kısıtlamasında ON DELETE RESTRICT seçeneği ne sağlar?", ["Bağlı alt kayıtlar varken ana kaydın silinmesini ENGELLER", "Alt kayıtları siler", "Alt kayıtları günceller", "Hepsini NULL yapar"], 0, "Veri Tabanı Tasarımı"),
    ("BCNF (Boyce-Codd Normal Form) hangi şartı gerektirir?", ["Her X -> Y fonksiyonel bağımlılığında X'in bir Süper Anahtar (Super Key) olması", "1NF olması yeterlidir", "Tabloda en az 5 kolon olması", "Yabancı anahtar bulunmaması"], 0, "Veri Tabanı Tasarımı"),
    ("4NF (Dördüncü Normal Form) hangi bağımlılık türünü ortadan kaldırmayı hedefler?", ["Çok Değerli Bağımlılıkları (Multivalued Dependencies)", "Kısmi bağımlılıkları", "Geçişli bağımlılıkları", "Atomik olmayan değerleri"], 0, "Veri Tabanı Tasarımı"),
    ("5NF (Beşinci Normal Form / PJNF) neyi hedefler?", ["Birleştirme Bağımlılıklarını (Join Dependencies) ortadan kaldırmayı", "FOREIGN KEY kullanımını", "İndeks sayısını artırmayı", "Tablo birleştirmeyi"], 0, "Veri Tabanı Tasarımı"),
    ("Relational Model'de 'Tuple' kelimesi neyi ifade eder?", ["Tablodaki bir SATIRI (Record)", "Tablodaki bir sütunu", "Veri tabanının kendisini", "Birincil anahtarı"], 0, "İlişkisel Cebir"),
    ("Relational Model'de 'Attribute' kelimesi neyi ifade eder?", ["Tablodaki bir SÜTUNU (Field)", "Tablodaki bir satırı", "İndeks ağacını", "Yabancı anahtarı"], 0, "İlişkisel Cebir"),
    ("Relational Model'de 'Relation' kelimesi veritabanında karşılık olarak neye denk gelir?", ["TABLO (Table)", "Sütun", "Satır", "Veri tipi"], 0, "İlişkisel Cebir"),
    ("Relational Algebra'da Intersection (Kesişim) hangi sembolle ifade edilir?", ["∩ (Kesişim)", "U (Birleşim)", "- (Fark)", "X (Çarpım)"], 0, "İlişkisel Cebir"),
    ("Relational Algebra'da Set Difference (Küme Farkı) hangi sembolle gösterilir?", ["- (Eksi / Fark)", "∩", "U", "σ"], 0, "İlişkisel Cebir"),
    ("SQL CROSS JOIN işlemi sonucunda elde edilen satır sayısı nedir?", ["Sol tablonun satır sayısı x Sağ tablonun satır sayısı", "Sol tablo satır sayısı + Sağ tablo satır sayısı", "Eşleşen satır sayısı", "Sıfır"], 0, "SQL Temelleri"),
    ("SELF JOIN hangi durumda kullanılır?", ["Bir tablonun KENDİ KENDİSİYLE birleştirilmesi gerektiğinde (örn: çalışan-yönetici ilişkisi)", "İki farklı veri tabanını birleştirirken", "Tablo silerken", "İndeks oluştururken"], 0, "SQL Temelleri"),
    ("SQL VIEW kullanmanın temel avantajlarından biri nedir?", ["Karmaşık sorguları basitleştirip güvenlik ve erişim kontrolü sağlaması", "Diskte daha az yer kaplaması", "Tabloları silmesi", "İndeks gereksinimini kaldırması"], 0, "SQL Temelleri"),
    ("Materialized View ile Standart View arasındaki temel fark nedir?", ["Materialized View sorgu sonucunu diskte fiziksel olarak saklar ve güncellenmesi gerekir", "Standart View diske yazılır", "Fark yoktur", "Materialized View SQLite'ta zorunludur"], 0, "SQLite & PostgreSQL"),
    ("Clustered Index (Kümeli İndeks) ile Non-Clustered Index farkı nedir?", ["Clustered Index verinin fiziksel disk sırasını belirler ve bir tabloda en fazla 1 adet olabilir", "Non-clustered tek adettir", "Fark yoktur", "Clustered indeks yapılmaz"], 0, "İndeksler & Performans"),
    ("SQLite'ta AUTOINCREMENT kullanmanın teknik etkisi nedir?", ["Silinen ID'lerin tekrar kullanılmasını engelleyen unseq rowid tablosunu tutar", "Tabloyu şifreler", "Sorguları 10 kat hızlandırır", "FOREIGN KEY'i kapatır"], 0, "SQLite & PostgreSQL"),
    ("SQL Subquery (Alt Sorgu) türlerinden Correlated Subquery nedir?", ["Dış sorgudaki satırlara bağımlı olarak her satır için tekrar çalışan alt sorgudur", "Bağımsız alt sorgudur", "Hızlı çalışan alt sorgudur", "Sadece SELECT'te kullanılır"], 0, "SQL Temelleri"),
    ("SQL DENSE_RANK() ile RANK() arasındaki fark nedir?", ["DENSE_RANK eşit puanlarda sıra numaralarında atlama (gap) yapmaz", "RANK sıra atlamaz", "İkisi tamamen aynıdır", "DENSE_RANK sıralama yapmaz"], 0, "SQL Temelleri"),
    ("SQL ROW_NUMBER() fonksiyonu ne işe yarar?", ["Sonuç kümesindeki her satıra benzersiz ardışık bir sayı atar", "Sadece çift sayıları verir", "NULL satırları sayar", "Tablo satır sayısını değiştirir"], 0, "SQL Temelleri"),
    ("SQL GROUP BY ile birlikte kullanılan GROUPING SETS ne sağlar?", ["Farklı boyutlarda birden fazla GROUP BY birleşimini tek sorguda yapmayı", "Veriyi silmeyi", "İndekslemeyi", "Şifrelemeyi"], 0, "SQL Temelleri"),
    ("PostgreSQL'de VACUUM komutunun görevi nedir?", ["Silinen veya güncellenen satırların bıraktığı ölü alanları temizleyip diski düzenlemek", "Veri tabanını sıfırlamak", "İndeks silmek", "Kullanıcıyı engellemek"], 0, "SQLite & PostgreSQL"),
    ("SQLite'ta VACUUM komutu ne işe yarar?", ["Veri tabanı dosyasını yeniden yapılandırarak kullanılmayan boş alanları diske geri kazandırır", "Verileri tamamen siler", "Tablo yapısını değiştirir", "Sadece RAM'i temizler"], 0, "SQLite & PostgreSQL"),
    ("Deadlock (Kilitlenme) veritabanında ne zaman oluşur?", ["İki farklı transaction'ın birbirinin kilitlediği kaynakları karşılıklı beklemesi durumunda", "Tablo silindiğinde", "Sorgu çok hızlı çalıştığında", "İndeks yoksa"], 0, "Veri Tabanı Tasarımı"),
    ("Two-Phase Locking (2PL) protokolünün amacı nedir?", ["Eşzamanlı (Concurrent) işlemlerin seri yapılabilirliğini (Serializability) garanti etmek", "İki tabloyu birleştirmek", "İki aşamada veri silmek", "İndeks oluşturmak"], 0, "Veri Tabanı Tasarımı"),
    ("Optimistic Concurrency Control ne zaman tercih edilir?", ["Çakışma (Conflict) ihtimalinin düşük olduğu ortamlarda kilit koymadan hızlı işlem için", "Her zaman", "Kilitlenmenin çok olduğu yerde", "Sadece SQLite'ta"], 0, "Veri Tabanı Tasarımı"),
    ("Pessimistic Concurrency Control ne zaman kullanılır?", ["Çakışma ihtimalinin yüksek olduğu yerlerde veriyi işlem öncesi kilitleyerek (Locking)", "Hiçbir zaman", "Sadece okuma yaparken", "İndeks oluştururken"], 0, "Veri Tabanı Tasarımı"),
    ("SQL'de Transaction'ı başlatmak için SQLite ve PostgreSQL'de hangi komut kullanılır?", ["BEGIN TRANSACTION (veya BEGIN)", "START DB", "OPEN TRANSACTION", "CREATE TRANSACTION"], 0, "SQL Temelleri"),
    ("SQL'de Savepoint ne anlama gelir?", ["Transaction içinde geri dönülebilecek ara kontrol noktaları tanımlar (ROLLBACK TO savepoint)", "Dosya yedekler", "Veri tabanını kaydeder", "Kullanıcı kaydeder"], 0, "SQL Temelleri"),
    ("SQL TRUNCATE TABLE ile DELETE FROM arasındaki temel fark nedir?", ["TRUNCATE tablodaki tüm verileri log tutmadan hızlıca siler ve ID'leri sıfırlar", "DELETE daha hızlıdır", "Fark yoktur", "TRUNCATE WHERE kullanabilir"], 0, "SQL Temelleri"),
    ("SQL'de CASE WHEN ifadesi ne işe yarar?", ["Sorgu içinde KOŞULLU MANTIKSAL (If-Else) ifadeler çalıştırmayı sağlar", "Tablo oluşturur", "Sadece döngü kurar", "İndeksleri sıralar"], 0, "SQL Temelleri"),
    ("Veri tabanında Entity Integrity (Varlık Bütünlüğü) kuralı neyi gerektirir?", ["Her tablonun bir birincil anahtara (Primary Key) sahip olmasını ve bunun NULL olamamasını", "FOREIGN KEY kullanımını", "İndeks açılmasını", "Sadece 3NF olmasını"], 0, "Veri Tabanı Tasarımı"),
    ("Referential Integrity (Referansel Bütünlük) kuralı nedir?", ["Yabancı anahtarın ya geçerli bir birincil anahtara işaret etmesini ya da NULL olmasını", "PRIMARY KEY kuralıdır", "E-posta formatıdır", "Sadece SQLite kuralıdır"], 0, "Veri Tabanı Tasarımı"),
    ("Domain Integrity (Etki Alanı Bütünlüğü) kuralı ne anlama gelir?", ["Bir sütuna sadece tanımlanan veri tipinde ve kısıtlar (CHECK) dahilinde değer girilmesi", "Tablo ismi kuralı", "Yabancı anahtar kuralı", "İndeks kuralı"], 0, "Veri Tabanı Tasarımı"),
    ("User-Defined Integrity (Kullanıcı Tanımlı Bütünlük) neyi kapsar?", ["İş mantığına özel yazılan CHECK kısıtları ve Trigger yapılarını", "Kullanıcı şifrelerini", "SQL komutlarını", "Sadece e-posta kontrolünü"], 0, "Veri Tabanı Tasarımı"),
    ("SQL STRING Aggregation (Group Concat) fonksiyonu SQLite'ta hangisidir?", ["GROUP_CONCAT(col, sep)", "STRING_AGG()", "LISTAGG()", "ARRAY_AGG()"], 0, "SQLite & PostgreSQL"),
    ("PostgreSQL'de metin birleştirme fonksiyonu hangisidir?", ["STRING_AGG(col, sep)", "GROUP_CONCAT()", "CONCAT_LIST()", "TEXT_JOIN()"], 0, "SQLite & PostgreSQL"),
    ("SQL'de INSTR(metin, aranan) fonksiyonu ne döndürür?", ["Aranan alt metnin başlangıç pozisyon index numarasını", "Metnin uzunluğunu", "Metni büyük harfe çevirir", "Metni siler"], 0, "SQL Temelleri"),
    ("SQL LENGTH(metin) veya CHAR_LENGTH() ne işe yarar?", ["Metnin karakter sayısını döndürür", "Metnin byte boyutunu verir", "Metni ters çevirir", "NULL yapar"], 0, "SQL Temelleri"),
    ("SQL UPPER() ve LOWER() fonksiyonları ne yapar?", ["Metni büyük veya küçük harfe dönüştürür", "Metni keser", "Metni sıralar", "Metni arar"], 0, "SQL Temelleri"),
    ("SQL SUBSTR(metin, baslangic, uzunluk) ne işe yarar?", ["Metinden belirtilen aralıktaki alt parçayı (substring) kesip alır", "Metni böler", "Metni siler", "Metni birleştirir"], 0, "SQL Temelleri"),
    ("SQL REPLACE(metin, eski, yeni) fonksiyonu ne yapar?", ["Metin içindeki eski karakter dizisini yenisiyle değiştirir", "Tabloyu yeniler", "Sütunu siler", "İndekslere basar"], 0, "SQL Temelleri"),
    ("SQLite'ta 'INTEGER PRIMARY KEY' kolonu AUTOINCREMENT olmadan kullanılırsa ne olur?", ["Silinen en yüksek ID'den büyük bir sonraki tamsayıyı (RowID) otomatik alır, ancak silinen alanlar kullanılabilir", "Hata verir", "ID üretmez", "NULL yapar"], 0, "SQLite & PostgreSQL"),
    ("SQL UNION kullanılırken iki sorgunun hangi özellikte olması zorunludur?", ["Sütun sayılarının ve uyumlu veri tiplerinin aynı olması", "Tablo isimlerinin aynı olması", "İndekslerinin aynı olması", "WHERE olmaması"], 0, "SQL Temelleri"),
    ("SQL INTERSECT operatörü ne döndürür?", ["İki SELECT sorgusunun ORTAK olan ortak satırlarını (Kesişim)", "Tüm satırları", "Farklı satırları", "Hiçbir şeyi"], 0, "SQL Temelleri"),
    ("SQL EXCEPT (veya MINUS) operatörü ne işe yarar?", ["İlk sorguda olup ikinci sorguda OLMAYAN satırları getirir (Küme Farkı)", "Kesişimi verir", "Hepsini toplar", "Tümünü siler"], 0, "SQL Temelleri"),
    ("SQLite veri tabanı dosyasını kilitleme (Database Locking) mantığı nedir?", ["SQLite dosya seviyesinde kilit koyar; yazma anında tüm veritabanı kilitlenebilir", "Satır seviyesinde kilit koyar", "Hiç kilit koymaz", "Sunucu kilitler"], 0, "SQLite & PostgreSQL"),
    ("PostgreSQL kilitleme (Locking) seviyesi nedir?", ["Satır (Row-level) ve Tablo seviyesinde gelişmiş eşzamanlı kilitleme sağlar", "Sadece dosya kilitler", "Kilit kullanmaz", "Sadece RAM kilitler"], 0, "SQLite & PostgreSQL"),
    ("SQL'de DROP ile TRUNCATE arasındaki fark nedir?", ["DROP tablo şemasını ve verisini tamamen siler; TRUNCATE şemayı korur sadece veriyi sıfırlar", "DROP daha hızlıdır", "TRUNCATE tabloyu tamamen siler", "Fark yoktur"], 0, "SQL Temelleri"),
    ("SQL'de 'PRIMARY KEY' ile 'UNIQUE' arasındaki en temel fark nedir?", ["PRIMARY KEY NULL değer alamaz ve tabloda tek adettir; UNIQUE ise NULL alabilir ve birden fazla tanımlanabilir", "UNIQUE tek adettir", "Fark yoktur", "PRIMARY KEY NULL alabilir"], 0, "Veri Tabanı Tasarımı"),
    ("SQLite'ta PRAGMA integrity_check komutu ne işe yarar?", ["Veri tabanındaki B-Tree indekslerinin ve dosya bütünlüğünün bozuk olup olmadığını denetler", "Verileri siler", "Yedek alır", "Tablo oluşturur"], 0, "SQLite & PostgreSQL"),
]

def generate_questions():
    """110 benzersiz soruyu seçenekleriyle döndürür."""
    questions = []
    labels = ["A", "B", "C", "D", "E"]
    
    # Tam olarak 110 soru al
    selected = RAW_QUESTIONS[:110]
    
    for idx, (qtext, opts, correct_idx, category) in enumerate(selected, start=1):
        difficulty = DIFFICULTIES[(idx - 1) % len(DIFFICULTIES)]
        points = 10.0 if difficulty == "kolay" else (15.0 if difficulty == "orta" else 20.0)
        
        formatted_opts = []
        for o_idx, opt_text in enumerate(opts):
            label = labels[o_idx] if o_idx < len(labels) else f"O{o_idx+1}"
            is_correct = 1 if o_idx == correct_idx else 0
            formatted_opts.append((label, opt_text, is_correct))
            
        questions.append((qtext, category, difficulty, points, formatted_opts))
        
    return questions

def seed_database():
    print("Veri tabanı bağlantısı kuruluyor ve şema yükleniyor...")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    
    cursor = conn.cursor()
    print("[OK] Şema başarıyla yüklendi.")

    # 1. KULLANICILAR (60 Adet)
    print("Kullanıcılar ekleniyor (Target: 50+)...")
    kullanicilar = []
    used_usernames = set()
    used_emails = set()

    for i in range(1, 61):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        fullname = f"{fn} {ln}"
        
        base_username = f"{fn.lower()}{ln.lower()}".replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
        username = base_username
        suffix = 1
        while username in used_usernames:
            username = f"{base_username}{suffix}"
            suffix += 1
        used_usernames.add(username)
        
        email = f"{username}@ogr.edu.tr"
        used_emails.add(email)
        
        reg_date = (datetime.now() - timedelta(days=random.randint(5, 90))).strftime("%Y-%m-%d %H:%M:%S")
        status = "aktif" if i <= 55 else ("pasif" if i <= 58 else "engelli")
        
        kullanicilar.append((username, email, fullname, reg_date, status))
        
    cursor.executemany("""
        INSERT INTO kullanicilar (kullanici_adi, eposta, ad_soyad, kayit_tarihi, durum)
        VALUES (?, ?, ?, ?, ?);
    """, kullanicilar)
    print(f"[OK] {cursor.rowcount} kullanıcı başarıyla eklendi.")

    # 2. OTURUMLAR (5 Adet)
    print("Oturumlar ekleniyor (Target: 5)...")
    now = datetime.now()
    oturumlar = [
        (
            "Veritabanı Sistemleri Temel Seviye Vize Quiz",
            "SQL temel komutları, DDL, DML ve basit WHERE sorgularını kapsayan quiz.",
            "tamamlandi",
            (now - timedelta(days=7, hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"),
            45,
            50.0
        ),
        (
            "SQL ve Relational Algebra İleri Seviye Quiz",
            "JOIN türleri, GROUP BY, HAVING, subquery ve ilişkisel cebir işlemleri.",
            "devam_ediyor",
            (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            None,
            60,
            60.0
        ),
        (
            "PostgreSQL & SQLite Veri Katmanı Performans Sınavı",
            "İndeksleme stratejileri, B-Tree, query optimization ve ACID prensipleri.",
            "planlandi",
            (now + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
            (now + timedelta(days=2, hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            30,
            50.0
        ),
        (
            "Yazılım Mimarisi ve Veri Tabanı Tasarımı Genel Değerlendirme",
            "Normalizasyon formları (1NF, 2NF, 3NF, BCNF), ER Diyagramı ve Varlık İlişkileri.",
            "tamamlandi",
            (now - timedelta(days=3, hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=3, hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            50,
            55.0
        ),
        (
            "Veri Tabanı Güvenliği, İndeksler ve İlelebet İletişim Quiz",
            "Veri tabanı güvenlik açıkları, SQL Injection ve yetkilendirme modelleri.",
            "iptal",
            (now - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S"),
            40,
            50.0
        )
    ]

    cursor.executemany("""
        INSERT INTO oturumlar (baslik, aciklama, durum, baslangic_zaman, bitis_zaman, sure_dakika, gecme_notu)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, oturumlar)
    print(f"[OK] {cursor.rowcount} oturum eklendi.")

    # 3. SORULAR & SECENEKLER (110 Tamamen Benzersiz Soru + Seçenekler)
    print("110 Benzersiz Soru ve seçenekler ekleniyor...")
    questions_list = generate_questions()
    
    question_count = 0
    option_count = 0
    
    for qtext, cat, diff, pts, opts in questions_list:
        cursor.execute("""
            INSERT INTO sorular (soru_metni, kategori, zorluk_seviyesi, puan_degeri)
            VALUES (?, ?, ?, ?);
        """, (qtext, cat, diff, pts))
        
        soru_id = cursor.lastrowid
        question_count += 1
        
        for label, opt_text, is_correct in opts:
            cursor.execute("""
                INSERT INTO secenekler (soru_id, secenek_etiketi, secenek_metni, dogru_mu)
                VALUES (?, ?, ?, ?);
            """, (soru_id, label, opt_text, is_correct))
            option_count += 1

    print(f"[OK] {question_count} benzersiz soru ve {option_count} seçenek eklendi.")

    # 4. OTURUM-SORU EŞLEŞTİRMELERİ (oturum_sorulari)
    print("Sorular oturumlara atanıyor...")
    session_assignments = [
        (1, list(range(1, 26))),
        (2, list(range(21, 46))),
        (3, list(range(46, 71))),
        (4, list(range(71, 96))),
        (5, list(range(91, 111)))
    ]
    
    total_assignments = 0
    for oturum_id, soru_ids in session_assignments:
        for sira, soru_id in enumerate(soru_ids, start=1):
            cursor.execute("""
                INSERT INTO oturum_sorulari (oturum_id, soru_id, soru_sirasi)
                VALUES (?, ?, ?);
            """, (oturum_id, soru_id, sira))
            total_assignments += 1
            
    print(f"[OK] {total_assignments} soru-oturum eşleştirmesi yapıldı.")

    # 5. KATILIMLAR & CEVAPLAR
    print("Örnek katılım ve cevap kayıtları oluşturuluyor...")
    enrollment_count = 0
    answer_count = 0

    # Oturum 1 Katılımları (1..40 kullanıcılar)
    for u_id in range(1, 41):
        cursor.execute("""
            INSERT INTO katilimlar (kullanici_id, oturum_id, katilim_zaman, tamamlama_zaman, tamamlandi_mi)
            VALUES (?, 1, datetime('now', '-7 days', '+5 minutes'), datetime('now', '-7 days', '+40 minutes'), 1);
        """, (u_id,))
        katilim_id = cursor.lastrowid
        enrollment_count += 1
        
        cursor.execute("SELECT soru_id FROM oturum_sorulari WHERE oturum_id = 1 ORDER BY soru_sirasi;")
        session_questions = cursor.fetchall()
        
        for (sq_id,) in session_questions:
            if random.random() < 0.85:
                cursor.execute("SELECT secenek_id, dogru_mu FROM secenekler WHERE soru_id = ?;", (sq_id,))
                opts = cursor.fetchall()
                
                if random.random() < 0.70:
                    chosen = [o[0] for o in opts if o[1] == 1][0]
                else:
                    wrong_opts = [o[0] for o in opts if o[1] == 0]
                    chosen = random.choice(wrong_opts) if wrong_opts else opts[0][0]
                    
                cursor.execute("""
                    INSERT INTO cevaplar (katilim_id, kullanici_id, oturum_id, soru_id, secenek_id, cevaplama_zamani)
                    VALUES (?, ?, 1, ?, ?, datetime('now', '-7 days', '+10 minutes'));
                """, (katilim_id, u_id, sq_id, chosen))
                answer_count += 1

    # Oturum 2 Katılımları (Devam Ediyor - 15..45 kullanıcılar)
    for u_id in range(15, 46):
        cursor.execute("""
            INSERT INTO katilimlar (kullanici_id, oturum_id, katilim_zaman, tamamlama_zaman, tamamlandi_mi)
            VALUES (?, 2, datetime('now', '-45 minutes'), NULL, 0);
        """, (u_id,))
        katilim_id = cursor.lastrowid
        enrollment_count += 1
        
        cursor.execute("SELECT soru_id FROM oturum_sorulari WHERE oturum_id = 2 ORDER BY soru_sirasi;")
        session_questions = cursor.fetchall()
        
        answered_q_count = random.randint(5, 18)
        for sq_id, in session_questions[:answered_q_count]:
            cursor.execute("SELECT secenek_id, dogru_mu FROM secenekler WHERE soru_id = ?;", (sq_id,))
            opts = cursor.fetchall()
            if random.random() < 0.75:
                chosen = [o[0] for o in opts if o[1] == 1][0]
            else:
                wrong_opts = [o[0] for o in opts if o[1] == 0]
                chosen = random.choice(wrong_opts) if wrong_opts else opts[0][0]
                
            cursor.execute("""
                INSERT INTO cevaplar (katilim_id, kullanici_id, oturum_id, soru_id, secenek_id, cevaplama_zamani)
                VALUES (?, ?, 2, ?, ?, datetime('now', '-20 minutes'));
            """, (katilim_id, u_id, sq_id, chosen))
            answer_count += 1

    # Oturum 4 Katılımları (Tamamlandı - 20..45 kullanıcılar)
    for u_id in range(20, 46):
        cursor.execute("""
            INSERT INTO katilimlar (kullanici_id, oturum_id, katilim_zaman, tamamlama_zaman, tamamlandi_mi)
            VALUES (?, 4, datetime('now', '-3 days', '+2 minutes'), datetime('now', '-3 days', '+48 minutes'), 1);
        """, (u_id,))
        katilim_id = cursor.lastrowid
        enrollment_count += 1
        
        cursor.execute("SELECT soru_id FROM oturum_sorulari WHERE oturum_id = 4 ORDER BY soru_sirasi;")
        session_questions = cursor.fetchall()
        
        for sq_id, in session_questions:
            if random.random() < 0.88:
                cursor.execute("SELECT secenek_id, dogru_mu FROM secenekler WHERE soru_id = ?;", (sq_id,))
                opts = cursor.fetchall()
                if random.random() < 0.65:
                    chosen = [o[0] for o in opts if o[1] == 1][0]
                else:
                    wrong_opts = [o[0] for o in opts if o[1] == 0]
                    chosen = random.choice(wrong_opts) if wrong_opts else opts[0][0]
                    
                cursor.execute("""
                    INSERT INTO cevaplar (katilim_id, kullanici_id, oturum_id, soru_id, secenek_id, cevaplama_zamani)
                    VALUES (?, ?, 4, ?, ?, datetime('now', '-3 days', '+25 minutes'));
                """, (katilim_id, u_id, sq_id, chosen))
                answer_count += 1

    conn.commit()
    print(f"[OK] {enrollment_count} katılım kaydı ve {answer_count} kullanıcı cevabı oluşturuldu.")
    print("\n--- SEED İŞLEMİ ÖZETİ ---")
    
    for table in ["kullanicilar", "oturumlar", "sorular", "secenekler", "oturum_sorulari", "katilimlar", "cevaplar"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        cnt = cursor.fetchone()[0]
        print(f"  • {table.capitalize()}: {cnt} kayıt")

    conn.close()
    print("Veri tabanı seeding işlemi başarıyla tamamlandı!\n")

if __name__ == "__main__":
    seed_database()
