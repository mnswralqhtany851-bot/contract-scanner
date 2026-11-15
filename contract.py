from flask import Flask, request, render_template_string
import re

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>كاشف العقود الذكي | تحليل البنود الموجودة والناقصة</title>
    <link href="https://googleapis.com" rel="stylesheet">
    <style>
        :root {
            --bg-main: #030712;
            --surface: rgba(17, 24, 39, 0.88);
            --border: rgba(255, 255, 255, 0.08);
            --border-bright: rgba(139, 92, 246, 0.5);
            --accent: #8b5cf6;
            --accent-light: #a78bfa;
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
            --safe: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'IBM Plex Sans Arabic', sans-serif; }
        body {
            background-color: var(--bg-main);
            background-image: radial-gradient(circle at 20% 10%, rgba(139, 92, 246, 0.16) 0%, transparent 45%);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        header {
            width: 100%; max-width: 1120px; padding: 22px 24px;
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 1px solid var(--border);
        }
        .brand { display: flex; align-items: center; gap: 12px; font-size: 20px; font-weight: 700; }
        .brand-icon {
            width: 36px; height: 36px; border-radius: 10px;
            background: linear-gradient(135deg, #7c3aed, #a78bfa);
            display: flex; align-items: center; justify-content: center;
        }
        .pro-badge {
            background: rgba(139, 92, 246, 0.14); border: 1px solid rgba(139, 92, 246, 0.35);
            color: var(--accent-light); padding: 7px 16px; border-radius: 999px; font-size: 13px; font-weight: 700;
            text-decoration: none; transition: transform 0.25s ease;
        }
        .pro-badge:hover { transform: translateY(-3px); }
        main { width: 100%; max-width: 950px; padding: 48px 20px; text-align: center; flex: 1; }
        .hero-tag {
            display: inline-block; padding: 6px 16px; border-radius: 999px;
            background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.25);
            color: var(--accent-light); font-size: 13px; font-weight: 600; margin-bottom: 18px;
        }
        h1 { font-size: 38px; font-weight: 700; line-height: 1.3; margin-bottom: 14px; color: #fff; }
        .subtitle { color: var(--text-muted); font-size: 17px; max-width: 670px; margin: 0 auto 36px; line-height: 1.6; }
        .editor-box {
            background: var(--surface); border: 1px solid var(--border);
            padding: 24px; border-radius: 22px; margin-bottom: 38px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
            text-align: right;
        }
        .type-select {
            background: rgba(3, 7, 18, 0.9); border: 1px solid var(--border); color: #fff;
            padding: 13px 16px; border-radius: 12px; font-size: 15px; margin-bottom: 14px; width: 100%; outline: none;
        }
        .editor-box textarea {
            width: 100%; height: 195px; background: rgba(3, 7, 18, 0.75);
            border: 1px solid var(--border); color: #fff; font-size: 15px;
            padding: 16px; border-radius: 14px; outline: none; resize: vertical;
            line-height: 1.7; margin-bottom: 16px;
        }
        .editor-box textarea:focus { border-color: var(--border-bright); }
        .editor-footer { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px; }
        .btn-analyze {
            background: linear-gradient(135deg, #7c3aed, #a78bfa);
            color: #030712; border: none; padding: 14px 34px; border-radius: 12px;
            font-size: 16px; font-weight: 700; cursor: pointer;
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }
        .btn-analyze:hover { transform: translateY(-4px); box-shadow: 0 12px 24px -6px rgba(139, 92, 246, 0.5); }
        .report-panel {
            background: var(--surface); border: 1px solid var(--border);
            border-radius: 22px; padding: 32px; text-align: right; margin-bottom: 40px;
        }
        .panel-top {
            display: flex; justify-content: space-between; align-items: center;
            padding-bottom: 20px; margin-bottom: 24px; border-bottom: 1px solid var(--border);
            flex-wrap: wrap; gap: 16px;
        }
        .score-badge {
            width: 92px; height: 92px; border-radius: 18px;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            font-weight: 700; font-size: 26px; border: 2px solid;
        }
        .score-badge small { font-size: 11px; margin-top: 2px; }
        .safe-style { border-color: var(--safe); color: var(--safe); background: rgba(16, 185, 129, 0.08); }
        .warning-style { border-color: var(--warning); color: var(--warning); background: rgba(245, 158, 11, 0.08); }
        .danger-style { border-color: var(--danger); color: var(--danger); background: rgba(239, 68, 68, 0.08); }
        .sec-title { font-size: 17px; font-weight: 700; color: #fff; margin: 22px 0 12px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
        .risk-item {
            padding: 18px 20px; background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border); border-right: 4px solid var(--danger);
            border-radius: 12px; margin-bottom: 12px;
        }
        .risk-item.missing-item { border-right-color: var(--warning); background: rgba(245, 158, 11, 0.04); }
        .risk-item.safe-note { border-right-color: var(--safe); }
        .risk-item strong { display: block; font-size: 16px; margin-bottom: 6px; color: #fff; }
        .risk-item p { font-size: 14px; color: var(--text-muted); line-height: 1.6; margin-bottom: 8px; }
        .fix-box {
            background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.25);
            padding: 10px 14px; border-radius: 8px; font-size: 13px; color: #ddd6fe;
        }
        .paywall-box {
            margin-top: 24px; padding: 24px; border-radius: 16px;
            background: linear-gradient(135deg, rgba(124, 58, 237, 0.15), rgba(17, 24, 39, 0.9));
            border: 1px dashed var(--border-bright); text-align: center;
        }
        .btn-unlock {
            display: inline-block; margin-top: 14px; background: var(--accent-light); color: #030712;
            padding: 13px 28px; border-radius: 12px; text-decoration: none; font-weight: 700;
            transition: transform 0.25s ease;
        }
        .btn-unlock:hover { transform: translateY(-3px); }
        footer { width: 100%; text-align: center; padding: 22px; color: #6b7280; font-size: 13px; border-top: 1px solid var(--border); margin-top: 50px; }
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <div class="brand-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#030712" stroke-width="2.5">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                </svg>
            </div>
            كاشف العقود الذكي
        </div>
        <a href="#pro" class="pro-badge">الباقة الكاملة • 19 ريال</a>
    </header>
    <main>
        <div class="hero-tag">الذكاء الاستنتاجي لكشف الفخاخ والبنود المسكوت عنها</div>
        <h1>يكشف لك خطورة ما كُتب في العقد، وخطورة ما لم يُكتب عمداً</h1>
        <p class="subtitle">حتى لو أعطاك الطرف الآخر اتفاقية قصيرة بدون شروط واضحة، يحلل المحرك النص ويكشف لك الحقوق الناقصة التي يجب إضافتها فوراً.</p>

        <form class="editor-box" method="POST" action="/">
            <select name="contract_type" class="type-select">
                <option value="general" {{ 'selected' if c_type == 'general' else '' }}>عقد خدمات / مقاولة / شراء أو اتفاقية عمل حر</option>
                <option value="work" {{ 'selected' if c_type == 'work' else '' }}>عقد عمل وتوظيف (نظام العمل السعودي)</option>
                <option value="rent" {{ 'selected' if c_type == 'rent' else '' }}>عقد إيجار عقاري أو تجاري</option>
            </select>
            <textarea name="contract_text" placeholder="ألصق نص العقد أو حتى رسالة الاتفاق القصيرة هنا..." required>{{ contract_text }}</textarea>
            <div class="editor-footer">
                <span style="font-size: 13px; color: var(--text-muted);">التدقيق المجاني يشمل أول 500 حرف مع كشف البنود الناقصة مجاناً.</span>
                <button type="submit" class="btn-analyze">تحليل واستنتاج المخاطر</button>
            </div>
        </form>

        {% if result %}
        <div class="report-panel">
            <div class="panel-top">
                <div>
                    <span style="color: var(--text-muted); font-size: 13px;">تقرير الاستنتاج التعاقدي • تم تحليل {{ result.analyzed_chars }} حرف</span>
                    <h2 style="font-size: 22px; margin-top: 5px; color: {{ result.color }};">{{ result.title }}</h2>
                </div>
                <div class="score-badge {{ result.border_class }}">
                    {{ result.score }}%
                    <small>اكتمال الأمان</small>
                </div>
            </div>

            {% if result.missing_findings %}
            <div class="sec-title">ثغرات الغياب: حقوق وشروط أساسية غير موجودة في النص (خطر السكوت)</div>
            {% for item in result.missing_findings %}
            <div class="risk-item missing-item">
                <strong>{{ item.head }}</strong>
                <p>{{ item.detail }}</p>
                <div class="fix-box"><strong>بند مقترح لإضافته فوراً:</strong> {{ item.fix }}</div>
            </div>
            {% endfor %}
            {% endif %}

            <div class="sec-title">تحليل البنود والأرقام المكتوبة داخل النص</div>
            {% for item in result.findings %}
            <div class="risk-item {{ 'safe-note' if item.safe else '' }}">
                <strong>{{ item.head }}</strong>
                <p>{{ item.detail }}</p>
                {% if item.fix %}
                <div class="fix-box"><strong>الصياغة البديلة المقترحة:</strong> {{ item.fix }}</div>
                {% endif %}
            </div>
            {% endfor %}

            {% if result.is_truncated %}
            <div id="pro" class="paywall-box">
                <h3 style="font-size: 19px; color: #fff; margin-bottom: 6px;">النص الكامل يحتوي على {{ result.total_chars }} حرف — تم فحص الجزء المجاني فقط</h3>
                <p style="color: var(--text-muted); font-size: 14px;">لفتح التدقيق الشامل لكامل العقد والحصول على صياغة عقد متكامل يحمي حقوقك:</p>
                <a href="https://wa.me" target="_blank" class="btn-unlock">افتح التدقيق الكامل الآن • 19 ريال</a>
            </div>
            {% endif %}
        </div>
        {% endif %}
    </main>
    <footer>منصة كاشف العقود الذكي © 2026 • نظام استنتاج وتحليل المخاطر التعاقدية والمالية</footer>
</body>
</html>
"""
def analyze_contract(full_text, c_type):
    total_chars = len(full_text.strip())
    is_truncated = total_chars > 500
    text_to_scan = full_text.strip()[:500] if is_truncated else full_text.strip()

    score = 100
    findings = []
    missing_findings = []

    # 1. محرك كشف البنود الناقصة (ما سُكت عنه في العقد)
    essential_clauses = [
        {
            "types": ["general", "work", "rent"],
            "check_words": ["ريال", "مبلغ", "أجر", "راتب", "قيمة", "تكلفة", "سعر", "مقابل"],
            "penalty": 20,
            "head": "غياب تحديد المقابل المالي أو آلية الدفع بوضوح",
            "detail": "النص لا يحدد المبلغ المالي بدقة أو مواعيد السداد؛ ترك المقابل المالي غامضاً يؤدي غالباً إلى خلافات أو مطالبات إضافية غير متوقعة.",
            "fix": "يُحدد إجمالي المقابل المالي بمبلغ وقدره (....) ريال سعودي فقط، يُسدد على دفعات مرتبطة بالإنجاز أو في تاريخ محدد."
        },
        {
            "types": ["general", "rent"],
            "check_words": ["مدة", "تاريخ", "يوم", "شهر", "سنة", "تسليم", "انتهاء", "ينتهي"],
            "penalty": 20,
            "head": "غياب تحديد مدة العقد أو موعد التسليم النهائي",
            "detail": "عدم وجود تاريخ محدد للبدء والانتهاء أو التسليم يمنح الطرف المنفذ مفتاح المماطلة دون أن تملك حق مطالبته بالتأخير.",
            "fix": "يلتزم الطرف المنفذ بتسليم كامل الأعمال محل العقد في موعد أقصاه (....) يوم عمل من تاريخ توقيع هذا العقد."
        },
        {
            "types": ["general", "work", "rent"],
            "check_words": ["فسخ", "إنهاء", "إلغاء", "إخلال", "تقصير"],
            "penalty": 15,
            "head": "غياب بند يوضح حقك في الفسخ أو الاسترجاع عند التقصير",
            "detail": "لم يذكر العقد ماذا يحدث لو أخل الطرف الآخر بالتزاماته أو تأخر؛ بدون هذا البند ستجد صعوبة في استرداد أموالك أو إنهاء الاتفاق.",
            "fix": "في حال إخلال أحد الطرفين بالتزاماته وعدم تصحيحها خلال 7 أيام من إشعاره كتابياً، يحق للطرف المتضرر فسخ العقد واسترداد مستحقاته."
        },
        {
            "types": ["general"],
            "check_words": ["ضمان", "صيانة", "تعديل", "مراجعة", "جودة", "مواصفات"],
            "penalty": 15,
            "head": "غياب بند الضمان أو التعديلات بعد التسليم",
            "detail": "الاتفاقية تخلو من أي التزام بضمان جودة العمل أو إجراء التعديلات اللازمة بعد التسليم الأولي.",
            "fix": "يضمن الطرف الأول جودة الأعمال المنفذة ويلتزم بإجراء التعديلات المطلوبة وفق المواصفات المتفق عليها مجاناً خلال فترة الضمان."
        },
        {
            "types": ["work"],
            "check_words": ["ساعات العمل", "إجازة", "تأمين", "بدل", "نقل", "سكن"],
            "penalty": 15,
            "head": "نقص بيانات البدلات والإجازات وساعات العمل الأساسية",
            "detail": "عقد العمل يفتقر لتفصيل البدلات (السكن والنقل) أو رصيد الإجازات السنوية وساعات العمل الأسبوعية وفق نظام العمل السعودي.",
            "fix": "تُحدد ساعات العمل بـ 8 ساعات يومياً (48 ساعة أسبوعياً كحد أقصى) مع إجازة سنوية مدفوعة الأجر لا تقل عن 21 يوماً وبدل سكن ونقل محدد."
        }
    ]

    for clause in essential_clauses:
        if c_type in clause["types"]:
            if not any(w in text_to_scan for w in clause["check_words"]):
                score -= clause["penalty"]
                missing_findings.append({
                    "head": clause["head"],
                    "detail": clause["detail"],
                    "fix": clause["fix"]
                })

    # 2. محرك تحليل الأرقام والمدد المبالغ فيها داخل النص
    days_matches = re.findall(r'(\d+)\s*(?:يوم|يوماً|أيام)', text_to_scan)
    for d in days_matches:
        if int(d) > 90 and c_type == "work":
            score -= 20
            findings.append({
                "safe": False,
                "head": f"مخالفة نظامية في الأرقام: رصد مدة ({d} يوماً) تتجاوز الحد المعتاد",
                "detail": "في نظام العمل السعودي، فترة التجربة الأساسية هي 90 يوماً ولا يجوز تمديدها لأكثر من 180 يوماً وباتفاق مكتوب مستقل.",
                "fix": "تعديل المدة لتكون 90 يوماً وفق المادة 53 من نظام العمل السعودي."
            })

    # 3. محرك كشف البنود الخطيرة المكتوبة في النص
    danger_rules = [
        {
            "keywords": ["شرط جزائي", "غرامة", "تعويض مالي", "يلتزم بدفع"],
            "penalty": 20,
            "head": "تنبيه مالي: شرط جزائي أو غرامة تعويضية",
            "detail": "يتضمن النص غرامة مالية عند الانسحاب أو التأخر؛ تأكد من تساوي الشرط الجزائي على الطرفين وعدم تطبيقه في الظروف القاهرة.",
            "fix": "يُستحق التعويض فقط عند ثبوت التقصير العمدي وبعد إشعار كتابي بمهلة تصحيح لا تقل عن 15 يوماً."
        },
        {
            "keywords": ["يتجدد تلقائيا", "يتجدد تلقائياً", "تجديد تلقائي", "ما لم يخطر"],
            "penalty": 15,
            "head": "تنبيه مدة: بند التجديد التلقائي الإلزامي",
            "detail": "العقد يلزمك بفترة جديدة كاملة تلقائياً ما لم ترسل إشعاراً رسمياً قبل انتهائه.",
            "fix": "يتجدد هذا العقد بموافقة الطرفين الكتابية الصريحة قبل انتهائه بثلاثين يوماً."
        },
        {
            "keywords": ["تنازل", "إبراء ذمة", "لا يحق للطرف الثاني", "يسقط حقه"],
            "penalty": 30,
            "head": "خطر حرج: بند تنازل مسبق عن الحقوق أو إبراء ذمة",
            "detail": "التنازل المسبق عن الحقوق قبل استلام كامل المستحقات يُعد شرطاً مجحفاً ويحرمك من المطالبة بحقك مستقبلاً.",
            "fix": "حذف عبارة التنازل المسبق بالكامل، وربط المخالصة باستلام كامل المستحقات المالية."
        },
        {
            "keywords": ["غير قابل للاسترداد", "لا يسترد", "مبلغ غير مسترجع"],
            "penalty": 20,
            "head": "تنبيه دفعات: مبالغ مقدمة غير قابلة للاسترداد",
            "detail": "دفع مبالغ مقدمة غير مسترجعة يعرضك للخسارة إذا تقاعس الطرف الآخر عن تنفيذ العمل.",
            "fix": "تُربط الدفعات بمراحل الإنجاز الفعلية، وتُسترد الدفعة المقدمة في حال عدم التزام الطرف المنفذ بالبدء."
        }
    ]

    for rule in danger_rules:
        if any(kw in text_to_scan for kw in rule["keywords"]):
            score -= rule["penalty"]
            findings.append({"safe": False, "head": rule["head"], "detail": rule["detail"], "fix": rule["fix"]})

    if not findings:
        findings.append({
            "safe": True,
            "head": "لم تُرصد صياغات عدوانية أو شروط جزائية صريحة في الكلمات المكتوبة",
            "detail": "الكلمات المكتوبة لا تحتوي على فخاخ ظاهرة، ولكن راجع قسم (ثغرات الغياب) أعلاه للتأكد من إضافة البنود الناقصة.",
            "fix": None
        })

    score = max(10, min(100, score))

    if score >= 80:
        title, color, border_class = "العقد مكتمل ومتوازن بنسبة عالية", "#10b981", "safe-style"
    elif score >= 50:
        title, color, border_class = "العقد ناقص أو يحتوي بنوداً تتطلب تعديلاً قبل التوقيع", "#f59e0b", "warning-style"
    else:
        title, color, border_class = "تحذير مرتفع: العقد غير آمن أو يفتقر لأهم حقوقك", "#ef4444", "danger-style"

    return {
        "score": score,
        "title": title,
        "color": color,
        "border_class": border_class,
        "findings": findings,
        "missing_findings": missing_findings,
        "total_chars": total_chars,
        "analyzed_chars": len(text_to_scan),
        "is_truncated": is_truncated
    }

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    contract_text = ""
    c_type = "general"
    if request.method == 'POST':
        contract_text = request.form.get('contract_text', '')
        c_type = request.form.get('contract_type', 'general')
        if contract_text.strip():
            result = analyze_contract(contract_text, c_type)
    return render_template_string(HTML_TEMPLATE, result=result, contract_text=contract_text, c_type=c_type)

if __name__ == '__main__':
    app.run(debug=True)
