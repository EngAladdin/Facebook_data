from flask import Flask, request, render_template_string, jsonify
import csv
import re
import os

app = Flask(__name__)

# ============================================
# إعدادات ملف البيانات
# ============================================
CSV_FILE = "full_data_part1.csv" # اسم ملف البيانات الجديد

# ============================================
# تحميل البيانات من ملف CSV
# ============================================
DATABASE = []

def load_data_from_csv():
    """تحميل البيانات من ملف CSV بالتنسيق الجديد"""
    global DATABASE
    all_data = []
    
    print("\n" + "="*50)
    print("📥 جاري تحميل البيانات من ملف CSV...")
    print("="*50)
    
    if not os.path.exists(CSV_FILE):
        print(f"❌ ملف {CSV_FILE} غير موجود!")
        print("📌 الرجاء التأكد من وجود الملف في نفس المجلد")
        return []
    
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # طباعة أسماء الأعمدة الموجودة
            print(f"📋 الأعمدة الموجودة: {list(reader.fieldnames)}")
            
            for row in reader:
                # استخراج البيانات من الأعمدة
                phone = row.get('phone', '').strip()
                user_id = row.get('user_id', '').strip()
                first_name = row.get('first_name', '').strip()
                last_name = row.get('last_name', '').strip()
                gender = row.get('gender', '').strip()
                city = row.get('city', '').strip()
                origin = row.get('origin', '').strip()
                status = row.get('status', '').strip()
                work = row.get('work', '').strip()
                date_added = row.get('date_added', '').strip()
                
                # دمج الاسم الأول والثاني
                full_name = f"{first_name} {last_name}".strip()
                if not full_name:
                    full_name = first_name or last_name or ''
                
                # تنظيف رقم الهاتف (إزالة +62 أو 62)
                clean_phone = phone
                if clean_phone.startswith('62'):
                    clean_phone = '0' + clean_phone[2:]
                elif clean_phone.startswith('+62'):
                    clean_phone = '0' + clean_phone[3:]
                
                # إضافة السجل إلى قاعدة البيانات
                record = {
                    'phone': clean_phone,
                    'id': user_id,
                    'name': full_name,
                    'first_name': first_name,
                    'last_name': last_name,
                    'gender': gender,
                    'city': city,
                    'origin': origin,
                    'status': status,
                    'work': work,
                    'date_added': date_added
                }
                all_data.append(record)
        
        print(f"✅ تم تحميل {len(all_data)} سجل من {CSV_FILE}")
        
        # عرض عينة من البيانات
        if all_data:
            print("\n📊 عينة من البيانات (أول 3 سجلات):")
            for i, record in enumerate(all_data[:3]):
                print(f"   {i+1}. {record['phone']} | {record['id']} | {record['name']}")
        
    except Exception as e:
        print(f"❌ خطأ في تحميل الملف: {e}")
        return []
    
    print("="*50)
    return all_data

# ============================================
# دوال البحث
# ============================================

def search_by_phone(phone):
    """البحث برقم الهاتف"""
    clean = re.sub(r'[^\d]', '', phone)
    clean = re.sub(r'^(62|0)?', '', clean)
    
    for record in DATABASE:
        record_phone = re.sub(r'[^\d]', '', record['phone'])
        record_phone = re.sub(r'^(62|0)?', '', record_phone)
        if clean == record_phone or phone in record['phone']:
            return record
    return None

def search_by_id(search_id):
    """البحث بالمعرف (user_id)"""
    clean = search_id.strip()
    for record in DATABASE:
        if clean == record['id']:
            return record
    return None

def search_by_name(name):
    """البحث بالاسم (first_name, last_name, أو الاسم الكامل)"""
    clean = name.strip().lower()
    for record in DATABASE:
        if (clean in record['name'].lower() or 
            clean in record['first_name'].lower() or 
            clean in record['last_name'].lower()):
            return record
    return None

def search_by_city(city):
    """البحث بالمدينة"""
    clean = city.strip().lower()
    for record in DATABASE:
        if clean in record['city'].lower():
            return record
    return None

def search(query):
    """البحث في جميع الحقول"""
    # البحث برقم الهاتف
    result = search_by_phone(query)
    if result:
        return result
    
    # البحث بالمعرف
    result = search_by_id(query)
    if result:
        return result
    
    # البحث بالاسم
    result = search_by_name(query)
    if result:
        return result
    
    # البحث بالمدينة
    result = search_by_city(query)
    if result:
        return result
    
    return None

# ============================================
# قالب HTML المعدل
# ============================================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>البحث عن بيانات المستخدمين</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Tahoma', 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1877f2 0%, #0e5a8a 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        .header {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .header h1 { color: #1877f2; margin-bottom: 10px; }
        .subtitle { color: #666; font-size: 14px; }
        .search-card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .search-box { display: flex; gap: 10px; flex-wrap: wrap; }
        .search-box input {
            flex: 1;
            padding: 15px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-family: monospace;
            direction: ltr;
            text-align: left;
        }
        .search-box input:focus { outline: none; border-color: #1877f2; }
        .search-box button {
            padding: 15px 30px;
            background: #1877f2;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
            font-weight: bold;
        }
        .result-card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            display: none;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .result-card.show { display: block; animation: fadeIn 0.3s; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        .result-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #1877f2;
        }
        .result-header .icon { font-size: 30px; }
        .result-header h2 { color: #1877f2; }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }
        .info-row {
            display: flex;
            padding: 10px;
            background: #f5f5f5;
            border-radius: 10px;
        }
        .info-label {
            width: 100px;
            font-weight: bold;
            color: #555;
        }
        .info-value {
            flex: 1;
            color: #333;
            word-break: break-all;
        }
        .fb-link {
            display: inline-block;
            margin-top: 15px;
            padding: 10px 20px;
            background: #1877f2;
            color: white;
            text-decoration: none;
            border-radius: 8px;
        }
        .not-found { text-align: center; padding: 30px; color: #dc3545; }
        .loading { display: none; text-align: center; padding: 20px; }
        .loading.show { display: block; }
        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #ddd;
            border-top: 4px solid #1877f2;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .stats { text-align: center; font-size: 12px; color: rgba(255,255,255,0.7); margin-top: 20px; }
        .search-tips {
            background: #e3f2fd;
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
            font-size: 13px;
            color: #1565c0;
        }
        .search-tips ul { margin-right: 20px; margin-top: 10px; }
        @media (max-width: 700px) {
            .info-grid { grid-template-columns: 1fr; }
            .info-row { flex-direction: column; }
            .info-label { width: 100%; margin-bottom: 5px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 البحث عن بيانات المستخدمين</h1>
            <div class="subtitle">ابحث باستخدام رقم الهاتف أو المعرف أو الاسم</div>
        </div>
        
        <div class="search-card">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="مثال: 62816105226 أو 1639263955 أو Prakoso" autocomplete="off">
                <button onclick="search()" id="searchBtn">🔎 بحث</button>
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <div>جاري البحث...</div>
            </div>
            
            <div class="search-tips">
                💡 <strong>طرق البحث:</strong>
                <ul>
                    <li>📱 <strong>رقم الهاتف:</strong> 62816105226 أو 0816105226</li>
                    <li>🆔 <strong>المعرف:</strong> 1639263955</li>
                    <li>👤 <strong>الاسم:</strong> Prakoso أو Wibowo</li>
                    <li>🏙️ <strong>المدينة:</strong> Jakarta</li>
                </ul>
            </div>
        </div>
        
        <div class="result-card" id="resultCard">
            <div class="result-header">
                <span class="icon">✅</span>
                <h2>نتيجة البحث</h2>
            </div>
            <div id="resultContent"></div>
        </div>
        
        <div class="stats">📊 قاعدة البيانات تحتوي على {{ db_count }} سجل</div>
    </div>
    
    <script>
        async function search() {
            const query = document.getElementById('searchInput').value.trim();
            if (!query) { alert('الرجاء إدخال رقم الهاتف أو المعرف أو الاسم'); return; }
            
            const btn = document.getElementById('searchBtn');
            const loading = document.getElementById('loading');
            const resultCard = document.getElementById('resultCard');
            
            btn.disabled = true;
            loading.classList.add('show');
            resultCard.classList.remove('show');
            
            try {
                const response = await fetch('/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });
                const result = await response.json();
                displayResult(result);
            } catch (error) {
                showError('حدث خطأ في الاتصال بالخادم');
            } finally {
                btn.disabled = false;
                loading.classList.remove('show');
            }
        }
        
        function displayResult(result) {
            const content = document.getElementById('resultContent');
            const resultCard = document.getElementById('resultCard');
            
            if (result.found) {
                content.innerHTML = `
                    <div class="info-grid">
                        <div class="info-row"><div class="info-label">📱 رقم الهاتف:</div><div class="info-value">${escapeHtml(result.phone)}</div></div>
                        <div class="info-row"><div class="info-label">🆔 المعرف:</div><div class="info-value">${escapeHtml(result.id)}</div></div>
                        <div class="info-row"><div class="info-label">👤 الاسم الأول:</div><div class="info-value">${escapeHtml(result.first_name)}</div></div>
                        <div class="info-row"><div class="info-label">👤 الاسم الأخير:</div><div class="info-value">${escapeHtml(result.last_name)}</div></div>
                        <div class="info-row"><div class="info-label">⚥ الجنس:</div><div class="info-value">${escapeHtml(result.gender) || '-'}</div></div>
                        <div class="info-row"><div class="info-label">🏙️ المدينة:</div><div class="info-value">${escapeHtml(result.city) || '-'}</div></div>
                        <div class="info-row"><div class="info-label">📍 الأصل:</div><div class="info-value">${escapeHtml(result.origin) || '-'}</div></div>
                        <div class="info-row"><div class="info-label">💍 الحالة:</div><div class="info-value">${escapeHtml(result.status) || '-'}</div></div>
                        <div class="info-row"><div class="info-label">💼 العمل:</div><div class="info-value">${escapeHtml(result.work) || '-'}</div></div>
                        <div class="info-row"><div class="info-label">📅 تاريخ الإضافة:</div><div class="info-value">${escapeHtml(result.date_added) || '-'}</div></div>
                    </div>
                    <a href="https://www.facebook.com/${escapeHtml(result.id)}" target="_blank" class="fb-link">🔗 عرض حساب فيسبوك</a>
                `;
            } else {
                content.innerHTML = `<div class="not-found">❌ لم يتم العثور على: "${escapeHtml(result.query)}"</div>`;
            }
            resultCard.classList.add('show');
        }
        
        function showError(msg) {
            const content = document.getElementById('resultContent');
            content.innerHTML = `<div class="not-found">⚠️ ${msg}</div>`;
            document.getElementById('resultCard').classList.add('show');
        }
        
        function escapeHtml(text) {
            if (!text) return '';
            return text.replace(/[&<>]/g, function(m) {
                if (m === '&') return '&amp;';
                if (m === '<') return '&lt;';
                if (m === '>') return '&gt;';
                return m;
            });
        }
        
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') search();
        });
    </script>
</body>
</html>
'''

# ============================================
# تحميل البيانات عند بدء التشغيل
# ============================================
print("\n🚀 بدء تشغيل خادم البحث...")
DATABASE = load_data_from_csv()

# ============================================
# Routes
# ============================================

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, db_count=len(DATABASE))

@app.route('/search', methods=['POST'])
def search_api():
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'found': False, 'error': 'No query provided'})
    
    result = search(query)
    
    if result:
        return jsonify({
            'found': True,
            'phone': result['phone'],
            'id': result['id'],
            'name': result['name'],
            'first_name': result['first_name'],
            'last_name': result['last_name'],
            'gender': result['gender'],
            'city': result['city'],
            'origin': result['origin'],
            'status': result['status'],
            'work': result['work'],
            'date_added': result['date_added'],
            'query': query
        })
    else:
        return jsonify({'found': False, 'query': query})

# ============================================
# التشغيل
# ============================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
