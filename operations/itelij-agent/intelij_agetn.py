import subprocess
import os
import platform

class IntelliJAgent:
    def __init__(self):
        self.system = platform.system()
        
    def find_intellij_path(self):
        """Определяет путь к исполняемому файлу IntelliJ IDEA в зависимости от операционной системы"""
        if self.system == "Windows":
            # Стандартный путь для Windows
            return r"C:\Program Files\JetBrains\IntelliJ IDEA\bin\idea64.exe"
        elif self.system == "Darwin":  # MacOS
            return "/Applications/IntelliJ IDEA.app/Contents/MacOS/idea"
        else:  # Linux
            return "/opt/intellij-idea/bin/idea.sh"
    
    def open_project(self, project_path):
        """Открывает указанный проект в IntelliJ IDEA"""
        try:
            intellij_path = self.find_intellij_path()
            if not os.path.exists(intellij_path):
                raise FileNotFoundError(f"IntelliJ IDEA не найден по пути: {intellij_path}")
                
            # Формируем команду для открытия проекта
            command = [intellij_path, project_path]
            
            # Запускаем процесс
            subprocess.Popen(command)
            print(f"Проект успешно открыт: {project_path}")
            
        except Exception as e:
            print(f"Ошибка при открытии проекта: {str(e)}")

def main():
    # Пример использования
    agent = IntelliJAgent()
    project_path = "путь/к/вашему/проекту/resource_manager"
    agent.open_project(project_path)

if __name__ == "__main__":
    main()