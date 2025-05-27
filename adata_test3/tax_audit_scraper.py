import re
from PyPDF2 import PdfReader

# Загрузка PDF
reader = PdfReader("document.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text()

# Поиск БИНов (12 цифр подряд)
bins = re.findall(r'\b\d{12}\b', text)

# Удаление дубликатов и сортировка
bins = sorted(set(bins))

# Сохранение в txt
with open("bins.txt", "w") as f:
    for bin_number in bins:
        f.write(bin_number + "\n")

print("Готово! Сохранено в bins.txt")
