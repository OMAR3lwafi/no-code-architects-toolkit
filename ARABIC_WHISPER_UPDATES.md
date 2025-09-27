# تحديثات Whisper للغة العربية

## ملخص التعديلات

تم تحديث جميع ملفات Whisper في المشروع لضمان استخدام اللغة العربية بشكل افتراضي وتحسين جودة الترجمة، مع اعتماد مصنع نماذج موحد (Factory) وحقن التبعية.

## الملفات المُعدّلة

### 1. `services/ass_toolkit.py`
- تم استبدال التحميل المباشر للنموذج بالاستخدام عبر `get_whisper_model(size="large")`
- تغيير القيمة الافتراضية من `language='auto'` إلى فرض العربية عند `auto`
- تمرير اللغة دائماً ضمن `transcription_options`

### 2. `services/transcription.py`  
- استخدام `get_whisper_model(size="large")` بدل التحميل المباشر
- تمرير `language=code` في جميع استدعاءات `model.transcribe(...)`
- إضافة Log: `Detected language: ...`

### 3. `services/v1/media/media_transcribe.py`
- استخدام المصنع `get_whisper_model(size="large")` وحقن التبعية
- ضبط اللغة دائماً عبر `options["language"] = code`

### 4. `Dockerfile`
- تم تغيير الـ warmup إلى `whisper.load_model('large')`
## التحقق من التعديلات

```bash
# شغّل سكريبت التحقق
./test_arabic_setup.sh
```
# أو تحقق يدوياً:
grep -r "language.*ar" services/     # يجب أن يظهر عدة مراجع
grep -r 'load_model("base")' services/   # يجب ألا يظهر أي نتائج
grep -r 'load_model("medium")' services/ # يجب ألا يظهر أي نتائج داخل services/
grep -r 'get_whisper_model' services/     # يجب أن يظهر في الملفات الثلاثة
1. **اللغة الافتراضية**: سيتم استخدام العربية (`ar`) تلقائياً
2. **جودة أفضل**: النموذج `medium` أدق من `base`  
3. **سرعة معقولة**: `medium` أسرع من `large` مع جودة جيدة
4. **Logs واضحة**: ستظهر رسائل مثل `Detected language: Arabic` أو تجاوز الكشف التلقائي

## اختبار سريع

```python
# اختبار مع فيديو عربي قصير (مثال)
from services.ass_toolkit import generate_transcription

# سيستخدم language="ar" تلقائياً  
result = generate_transcription("path/to/arabic/video.mp4")
print(result['text'])  # النص باللغة العربية
```

## ملاحظات

- إذا أردت استخدام لغة أخرى، مرر المعامل صراحة: `language="en"`
- لاستخدام نموذج أكبر، غيّر `"medium"` إلى `"large"` (يتطلب ذاكرة أكثر)
- في بيئة Production، تأكد من وجود ذاكرة كافية للنموذج `medium`

## التحسينات المستقبلية

- [ ] إضافة كشف تلقائي للغة مع fallback إلى العربية
- [ ] إضافة إعداد متغير البيئة لاختيار نموذج Whisper
- [ ] تحسين معالجة النصوص العربية (تشكيل، ترقيم)
