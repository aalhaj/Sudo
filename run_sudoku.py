#!/usr/bin/env python3
"""
Sudoku Game Launcher
برنامج تشغيل لعبة سودوكو الاحترافية
"""

import sys
import os
import argparse

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 6):
        print("❌ خطأ: يتطلب Python 3.6 أو أحدث")
        print(f"الإصدار الحالي: {sys.version}")
        sys.exit(1)

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import pygame
        print(f"✅ Pygame {pygame.version.ver} مثبت")
    except ImportError:
        print("❌ خطأ: مكتبة Pygame غير مثبتة")
        print("📦 لتثبيت Pygame، نفذ الأمر التالي:")
        print("   pip install pygame")
        sys.exit(1)

def show_game_info():
    """Display game information"""
    print("\n" + "="*60)
    print("🎮 لعبة سودوكو الاحترافية")
    print("="*60)
    print("📋 الميزات:")
    print("   • مولد ألغاز سودوكو صالحة")
    print("   • 4 مستويات صعوبة")
    print("   • واجهة رسومية تفاعلية")
    print("   • نظام تلميحات وملاحظات")
    print("   • إحصائيات اللعب")
    print("   • عدة ثيمات للعرض")
    print("\n🎮 عناصر التحكم:")
    print("   • الماوس: اختيار الخلايا")
    print("   • الأرقام 1-9: إدخال أرقام")
    print("   • Delete/Backspace: مسح محتوى")
    print("   • N: تبديل وضع الملاحظات")
    print("   • T: تبديل الثيم")
    print("="*60)

def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(description='Sudoku Game Launcher')
    parser.add_argument('--version', action='version', version='Sudoku Game 1.0')
    parser.add_argument('--enhanced', action='store_true', 
                       help='تشغيل النسخة المحسنة مع الميزات الإضافية')
    parser.add_argument('--basic', action='store_true',
                       help='تشغيل النسخة الأساسية')
    
    args = parser.parse_args()
    
    # Check requirements
    check_python_version()
    check_dependencies()
    
    # Show game info
    show_game_info()
    
    try:
        if args.basic:
            print("🎮 تشغيل النسخة الأساسية...")
            from sudoku_game import SudokuGame
            game = SudokuGame()
        else:
            print("🎮 تشغيل النسخة المحسنة...")
            from sudoku_enhanced import SudokuGame
            game = SudokuGame()
        
        game.run()
        
    except KeyboardInterrupt:
        print("\n👋 تم إنهاء اللعبة بنجاح")
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        print("📞 الرجاء الإبلاغ عن المشكلة")
        sys.exit(1)

if __name__ == "__main__":
    main()