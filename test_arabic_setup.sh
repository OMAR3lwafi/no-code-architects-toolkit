#!/bin/bash

echo "🔍 فحص التعديلات على ملفات Whisper..."
echo "================================="

# Check if Arabic language is set in all transcribe calls
echo "1️⃣ فحص services/ass_toolkit.py:"
if grep -q "language.*ar" services/ass_toolkit.py; then
    echo "   ✅ تم تثبيت اللغة العربية"
else
    echo "   ❌ لم يتم تثبيت اللغة العربية"
fi

if grep -q 'get_whisper_model' services/ass_toolkit.py; then
    echo "   ✅ يتم استخدام مصنع النماذج get_whisper_model"
else
    echo "   ❌ لا يتم استخدام مصنع النماذج get_whisper_model"
fi

echo ""
echo "2️⃣ فحص services/transcription.py:"
if grep -q "language.*ar" services/transcription.py; then
    echo "   ✅ تم تثبيت اللغة العربية"
else
    echo "   ❌ لم يتم تثبيت اللغة العربية"
fi

if grep -q 'get_whisper_model' services/transcription.py; then
    echo "   ✅ يتم استخدام مصنع النماذج get_whisper_model"
else
    echo "   ❌ لا يتم استخدام مصنع النماذج get_whisper_model"
fi

echo ""
echo "3️⃣ فحص services/v1/media/media_transcribe.py:"
if grep -q "language.*ar" services/v1/media/media_transcribe.py; then
    echo "   ✅ تم تثبيت اللغة العربية"
else
    echo "   ❌ لم يتم تثبيت اللغة العربية"
fi

if grep -q 'get_whisper_model' services/v1/media/media_transcribe.py; then
    echo "   ✅ يتم استخدام مصنع النماذج get_whisper_model"
else
    echo "   ❌ لا يتم استخدام مصنع النماذج get_whisper_model"
fi

echo ""
echo "4️⃣ فحص Dockerfile:"
if grep -q 'load_model.*large' Dockerfile; then
    echo "   ✅ تم تحديث Dockerfile للنموذج large"
else
    echo "   ❌ لم يتم تحديث Dockerfile"
fi

echo ""
echo "🎯 فحص عدم وجود استدعاءات مباشرة داخل services/:"
base_count=$(grep -r 'load_model("base")' services/ | wc -l)
medium_count=$(grep -r 'load_model("medium")' services/ | wc -l)
if [ $base_count -eq 0 ]; then
    echo "   ✅ لا توجد استدعاءات قديمة للنموذج base"
else
    echo "   ❌ لا تزال هناك $base_count استدعاءات للنموذج base"
fi
if [ $medium_count -eq 0 ]; then
    echo "   ✅ لا توجد استدعاءات مباشرة للنموذج medium داخل services/ (يُستخدم المصنع بدلاً منه)"
else
    echo "   ⚠️ يوجد $medium_count استدعاء مباشر للنموذج medium داخل services/"
fi

echo ""
echo "📊 ملخص الفحص:"
echo "==============="

# Count Arabic language references
ar_count=$(grep -r "language.*ar" services/ | wc -l)
echo "📝 عدد مراجع اللغة العربية: $ar_count"

# Docker large warmup
docker_large_count=$(grep -r 'load_model.*large' Dockerfile | wc -l)
echo "🧰 Docker warmup large count: $docker_large_count"

echo ""
echo "🚀 لاختبار الإعدادات:"
echo "   python3 test_arabic_whisper.py"
